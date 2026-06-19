import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request

from bm25_index import BM25Index
from config import ADMIN_TOKEN
from db import load_db_pairs
from detector import build_topic_centroids
from embedder import embed_texts, format_doc, make_doc_hash, make_doc_id
from numpy_index import NumpyIndex
from router import router as rag_router
from seed import load_seed
from store import ensure_collection, get_embeddings, get_existing_hashes, upsert

# qa_cache shared across requests — populated at startup
# Strengths:
# Fast in-memory access to QA pairs for quick retrieval.
# Persistent vector storage in ChromaDB for scalable similarity search.

# Limitations for large-scale/production:
# In-memory cache (qa_cache["qa_pairs"]) may not scale for millions of documents
# or distributed systems.
# No real-time sync between memory and DB if data changes after startup.
# No advanced retrieval (e.g., hybrid search, filtering, sharding).
# Lacks user/session management, security, and distributed cache.
# Best practices for production RAG:

# Use a scalable vector DB (like ChromaDB, Pinecone, Weaviate, etc.) as the single
# source of truth.
# Implement efficient retrieval pipelines (possibly with hybrid search: vectors +
# metadata filters).
# Use distributed caching (e.g., Redis) if you need fast access to frequently used data.
# Keep your in-memory cache in sync with DB updates, or use the DB directly for retrieval.
# Add monitoring, logging, and error handling for robustness.
qa_cache: dict = {"qa_pairs": []}


def _merge(seed_pairs: list[dict], db_pairs: list[dict]) -> list[dict]:
    """Seed is the baseline. DB pairs are additive; DB wins on duplicate questions."""
    try:
        merged: dict[str, dict] = {p["question"]: p for p in seed_pairs}
    except KeyError as ex:
        raise ValueError(f"Seed pair missing 'question' field: {ex}") from ex

    added = 0
    overwritten = 0
    for p in db_pairs:
        try:
            if p["question"] in merged:
                overwritten += 1
            else:
                added += 1
            merged[p["question"]] = p
        except KeyError as ex:
            raise ValueError(f"DB pair missing 'question' field: {ex}") from ex

    print(f"[merge] seed={len(seed_pairs)}  db={len(db_pairs)}  "
          f"new={added}  overwritten={overwritten}  total={len(merged)}")
    return list(merged.values())


async def _sync_to_chroma(pairs: list[dict]) -> None:
    '''Syncs the given question-answer pairs to ChromaDB. generates unique IDs and
    hashes for each pair and checks which pairs are new or changed compared to
    existing entries in ChromaDB. Only new or changed pairs are embedded and
    upserted to ChromaDB, optimizing performance by avoiding unnecessary
    operations on unchanged data.'''
    for p in pairs:
        p["_id"] = make_doc_id(p["question"])
        p["_hash"] = make_doc_hash(p["question"], p["answer"])
        p["_text"] = format_doc(p["question"], p["answer"], p.get("tags", []))

    # has try/catch for connection issues, will raise RuntimeError if ChromaDB is unreachable
    ensure_collection()
    existing = get_existing_hashes([p["_id"] for p in pairs])

    to_update = [
        p for p in pairs
        if p["_id"] not in existing or existing[p["_id"]] != p["_hash"]
    ]

    if not to_update:
        print(f"[chroma] all {len(pairs)} docs already up to date — skipping embed")
        return

    skip = len(pairs) - len(to_update)
    print(f"[chroma] embedding {len(to_update)} new/changed docs (skipping {skip} unchanged)")

    try:
        embeddings = await embed_texts([p["_text"] for p in to_update])
    except Exception as exc:
        print(f"[chroma] ERROR: embedding failed for batch of {len(to_update)} docs — "
              f"skipping upsert, ChromaDB will be stale until next reload. Reason: {exc}")
        return

    upsert(
        ids=[p["_id"] for p in to_update],
        documents=[p["_text"] for p in to_update],
        embeddings=embeddings,
        metadatas=[
            {
                "topic": p.get("topic", ""),
                "doc_hash": p["_hash"],
            }
            for p in to_update
        ],
    )
    print(f"[chroma] upserted {len(to_update)} docs")


"""
@asynccontextmanager
• decorator from contextlib for writing async context managers.
• Lets you manage setup and cleanup logic for resources (e.g., DB connections,
  caches) asynchronously.
• Code before 'yield' runs at startup (setup), code after 'yield' runs at
  shutdown (cleanup).
• Used by FastAPI for lifespan events (app startup/shutdown).
"""


async def _load_and_index(app: FastAPI, label: str = "startup", include_db: bool = True) -> dict:
    """Load seed + DB pairs, sync to Chroma, rebuild all indexes, update app.state.
    Returns a summary dict. Called at startup and by the /admin/reload endpoint."""
    from collections import Counter

    seed_pairs = load_seed()
    print(f"[{label}] step 1 — {len(seed_pairs)} pairs from seed.json")

    db_pairs = await load_db_pairs() if include_db else []
    qa_cache["qa_pairs"] = _merge(seed_pairs, db_pairs)
    print(f"[{label}] step 2 — {len(qa_cache['qa_pairs'])} pairs total after merge")
    topic_counts = Counter(p.get("topic", "unknown") for p in qa_cache["qa_pairs"])
    print(f"[{label}] topics in corpus: {dict(sorted(topic_counts.items()))}")
    db_sourced = [p for p in qa_cache["qa_pairs"] if p.get("source", "").startswith("db") or p.get("id", "").startswith("db-")]
    seed_sourced = len(qa_cache["qa_pairs"]) - len(db_sourced)
    print(f"[{label}] DB-sourced pairs in merged corpus: {len(db_sourced)}")

    try:
        await _sync_to_chroma(qa_cache["qa_pairs"])
        print(f"[{label}] step 3 — ChromaDB sync complete")
    except Exception as exc:
        print(f"[{label}] WARNING: ChromaDB sync failed — serving from memory only. Reason: {exc}")

    all_texts = [format_doc(p["question"], p["answer"], p.get("tags", []))
                 for p in qa_cache["qa_pairs"]]
    all_ids = [make_doc_id(p["question"]) for p in qa_cache["qa_pairs"]]
    all_topics = [p.get("topic", "unknown") for p in qa_cache["qa_pairs"]]
    topic_intro_ids: dict[str, str] = {}
    for p in qa_cache["qa_pairs"]:
        if "intro" not in p.get("tags", []):
            continue
        topic = p["topic"]
        doc_id = make_doc_id(p["question"])
        if topic in topic_intro_ids:
            print(f"[{label}] WARNING: duplicate intro tag for topic '{topic}' — "
                  f"keeping first, ignoring: {p['question'][:60]!r}")
            continue
        topic_intro_ids[topic] = doc_id
    print(f"[{label}] intro docs mapped: {sorted(topic_intro_ids.keys())}")

    all_embeddings: list[list[float]] = []
    topic_centroids: dict = {}
    try:
        stored = get_embeddings(all_ids)
        all_embeddings = [stored[id_] for id_ in all_ids if id_ in stored]
        if len(all_embeddings) != len(all_ids):
            raise ValueError(f"ChromaDB returned {len(all_embeddings)}/{len(all_ids)} embeddings")
        topic_centroids = build_topic_centroids(qa_cache["qa_pairs"], all_embeddings)
        print(f"[{label}] step 4 — topic centroids built: {sorted(topic_centroids.keys())}")
    except Exception as exc:
        print(f"[{label}] WARNING: centroid computation failed — topic detection disabled: {exc}")
        all_embeddings = []

    bm25 = BM25Index()
    try:
        bm25.build(documents=all_texts, ids=all_ids, topics=all_topics)
        vocab_size = len(bm25._bm25.idf) if bm25._bm25 else 0
        print(f"[{label}] step 5 — BM25 index built ({len(qa_cache['qa_pairs'])} docs, {vocab_size} unique tokens)")
    except Exception as exc:
        print(f"[{label}] ERROR: BM25 index build failed — sparse retrieval disabled: {exc}")

    numpy_idx = NumpyIndex()
    if all_embeddings:
        try:
            numpy_idx.build(
                ids=all_ids,
                embeddings=all_embeddings,
                topics=all_topics,
                documents=all_texts,
            )
            print(f"[{label}] step 6 — NumpyIndex built ({len(all_ids)} docs)")
        except Exception as exc:
            print(f"[{label}] ERROR: NumpyIndex build failed — dense retrieval disabled: {exc}")
    else:
        print(f"[{label}] step 6 — WARNING: NumpyIndex skipped (no embeddings)")

    id_to_topic = dict(zip(all_ids, all_topics))

    app.state.bm25 = bm25
    app.state.numpy_index = numpy_idx
    app.state.id_to_text = dict(zip(all_ids, all_texts))
    app.state.centroids = topic_centroids
    app.state.id_to_topic = id_to_topic
    app.state.topic_intro_ids = topic_intro_ids

    return {
        "total_docs": len(qa_cache["qa_pairs"]),
        "db_docs": len(db_sourced),
        "seed_docs": seed_sourced,
        "topics": dict(sorted(topic_counts.items())),
        "embeddings_ready": bool(all_embeddings),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):  # will run when the app starts and stops.
    await _load_and_index(app, label="startup", include_db=False)

    yield  # app runs and answers questions for users.

    # when app shutdown, clear the qa_cache to free memory: needed if used not in a
    # docker container, but in a serverless environment like AWS Lambda where the
    # same instance may be reused for multiple requests. Clearing the qa_cache on
    # shutdown helps prevent data leakage between requests and ensures that each
    # request starts with a clean slate.
    qa_cache["qa_pairs"] = []

# docker compose logs -f python-rag
app = FastAPI(lifespan=lifespan)
app.include_router(rag_router)


@app.post("/admin/reload-from-db")
async def admin_reload(request: Request) -> dict:
    """Re-load seed + DB pairs and rebuild all indexes without restarting.
    Requires X-Admin-Token header matching RAG_ADMIN_TOKEN env var."""
    if not ADMIN_TOKEN or request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    print("[reload] triggered via /admin/reload-from-db")
    summary = await _load_and_index(request.app, label="reload", include_db=True)
    return {"status": "ok", **summary}
app.state.load_and_index = _load_and_index


@app.get("/healthz")
def healthz(request: Request):
    numpy_idx: NumpyIndex = request.app.state.numpy_index
    bm25_idx: BM25Index = request.app.state.bm25
    return {
        "status": "ok",
        "qa_count": len(qa_cache["qa_pairs"]),
        "embeddings_ready": numpy_idx._matrix is not None,
        "bm25_ready": bm25_idx._bm25 is not None,
    }
