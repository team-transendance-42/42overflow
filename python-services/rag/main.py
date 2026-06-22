import asyncio
from collections import Counter
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import asyncpg

from bm25_index import BM25Index
from config import ADMIN_TOKEN, DB_URL
from db import load_db_pairs
from detector import build_topic_centroids
from dev_populate import clean_posts, ensure_subjects, ensure_users, insert_posts
from embedder import embed_texts, format_doc, make_doc_hash, make_doc_id
from numpy_index import NumpyIndex
from router import router as rag_router
from seed import load_seed
from store import get_embeddings, get_existing_hashes, upsert

# qa_cache shared across requests — populated at startup in ram from initial seed load in chromadb
# Strengths:
# Fast in-memory access to QA pairs for quick retrieval.
# Persistent vector storage in ChromaDB for scalable similarity search.(on start up or manual reload once we want to sync with DB(postgres) updates)

# Limitations for large-scale/production:
# In-memory cache (qa_cache["qa_pairs"]) may not scale for millions of documents
# or distributed systems.
# No real-time sync between memory and DB: needs to be done manually via /admin/sync-chroma endpoint, which may lead to stale data if DB updates are frequent.
# No advanced retrieval (e.g., hybrid search, filtering, sharding).: todo: check it out
# Lacks user/session management, security, and distributed cache: todo -> how vulnarable is: checkout
# Best practices for production RAG:

# Use a scalable vector DB (like ChromaDB, Pinecone, Weaviate, etc.) as the single
# source of truth.
# Implement efficient retrieval pipelines (possibly with hybrid search: vectors +
# metadata filters).todo: we already have it?
# Use distributed caching (e.g., Redis) if you need fast access to frequently used data.
# Keep your in-memory cache in sync with DB updates, or use the DB directly for retrieval.
# Add monitoring, logging, and error handling for robustness. todo
qa_cache: dict = {"qa_pairs": []}
_sync_lock = asyncio.Lock()


def require_admin(x_admin_token: str | None = Header(None)) -> None:
    """FastAPI dependency — raises 403 if X-Admin-Token header is missing or wrong."""
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")


class SeedRequest(BaseModel):
    clean: bool = False


async def _sync_to_chroma(pairs: list[dict]) -> dict[str, list[float]]:
    """Sync question-answer pairs to ChromaDB — only embeds new or changed docs.

    Returns {doc_id: embedding} for every doc that was freshly embedded this
    call. Empty dict when nothing changed or embedding failed. The caller uses
    this to avoid a redundant GET for docs whose vectors are already in memory."""
    augmented = [
        {
            **p,
            "_id":   make_doc_id(p["question"]),
            "_hash": make_doc_hash(p["question"], p["answer"]),
            "_text": format_doc(p["question"], p["answer"], p.get("tags", [])),
        }
        for p in pairs
    ]
    existing = get_existing_hashes([p["_id"] for p in augmented])

    to_update = [
        p for p in augmented
        if p["_id"] not in existing or existing[p["_id"]] != p["_hash"]
    ]

    if not to_update:
        print(f"[chroma] all {len(augmented)} docs already up to date — skipping embed")
        return {}

    skip = len(augmented) - len(to_update)
    print(f"[chroma] embedding {len(to_update)} new/changed docs (skipping {skip} unchanged)")

    try:
        embeddings = await embed_texts([p["_text"] for p in to_update])
    except Exception as exc:
        print(f"[chroma] ERROR: embedding failed for batch of {len(to_update)} docs — "
              f"skipping upsert, ChromaDB will be stale until next reload. Reason: {exc}")
        return {}

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
    return {p["_id"]: emb for p, emb in zip(to_update, embeddings)}


async def _load_pairs(include_db: bool, label: str) -> list[dict]:
    """Load seed + (optionally) Postgres pairs and validate required fields.

    Raises ValueError if any pair is missing 'question' or 'answer' — a
    malformed seed.json must fail loudly at startup rather than producing a
    silent KeyError deep inside _sync_to_chroma or the BM25 build."""
    seed_pairs = load_seed()
    print(f"[{label}] step 1 — {len(seed_pairs)} pairs from seed")

    db_pairs = await load_db_pairs() if include_db else []
    pairs = seed_pairs + db_pairs

    bad = [i for i, p in enumerate(pairs) if "question" not in p or "answer" not in p]
    if bad:
        raise ValueError(f"Pairs at indices {bad} missing required 'question' or 'answer' key")

    print(f"[{label}] step 2 — {len(pairs)} pairs total (seed={len(seed_pairs)} db={len(db_pairs)})")
    return pairs


def _prepare_corpus(pairs: list[dict], label: str) -> dict:
    """Single pass over pairs building all derived text structures.

    Doing this in one loop avoids calling format_doc and make_doc_id twice per
    pair (the old code called them once here and again inside _sync_to_chroma).
    Returns a dict with: all_texts, all_ids, all_topics, topic_intro_ids,
    id_to_text, id_to_topic."""
    all_texts: list[str] = []
    all_ids: list[str] = []
    all_topics: list[str] = []
    topic_intro_ids: dict[str, str] = {}

    for p in pairs:
        text = format_doc(p["question"], p["answer"], p.get("tags", []))
        doc_id = make_doc_id(p["question"])
        topic = p.get("topic", "unknown")

        all_texts.append(text)
        all_ids.append(doc_id)
        all_topics.append(topic)

        if "intro" in p.get("tags", []):
            if topic in topic_intro_ids:
                print(f"[{label}] WARNING: duplicate intro for topic '{topic}' — "
                      f"ignoring: {p['question'][:60]!r}")
            else:
                topic_intro_ids[topic] = doc_id

    print(f"[{label}] intro docs mapped: {sorted(topic_intro_ids.keys())}")
    return {
        "all_texts": all_texts,
        "all_ids": all_ids,
        "all_topics": all_topics,
        "topic_intro_ids": topic_intro_ids,
        "id_to_text": dict(zip(all_ids, all_texts)),
        "id_to_topic": dict(zip(all_ids, all_topics)),
    }


async def _fetch_embeddings(
    pairs: list[dict], all_ids: list[str], label: str
) -> tuple[list[list[float]], dict]:
    """Sync pairs to ChromaDB, fetch stored embeddings, build topic centroids.

    Returns ([], {}) on any ChromaDB or embedding failure so the caller can
    continue in degraded/BM25-only mode without crashing the startup path."""
    try:
        fresh = await _sync_to_chroma(pairs)
        print(f"[{label}] step 3 — ChromaDB sync complete ({len(fresh)} freshly embedded)")
    except Exception as exc:
        print(f"[{label}] WARNING: ChromaDB sync failed — serving from memory only. Reason: {exc}")
        return [], {}

    try:
        stale_ids = [id_ for id_ in all_ids if id_ not in fresh]
        stored = get_embeddings(stale_ids) if stale_ids else {}
        merged = {**stored, **fresh}
        all_embeddings = [merged[id_] for id_ in all_ids if id_ in merged]
        if len(all_embeddings) != len(all_ids):
            raise ValueError(f"ChromaDB returned {len(all_embeddings)}/{len(all_ids)} embeddings")
        topic_centroids = build_topic_centroids(pairs, all_embeddings)
        print(f"[{label}] step 4 — topic centroids built: {sorted(topic_centroids.keys())}")
        return all_embeddings, topic_centroids
    except Exception as exc:
        print(f"[{label}] WARNING: centroid computation failed — topic detection disabled: {exc}")
        return [], {}


def _build_indexes(
    corpus: dict,
    all_embeddings: list[list[float]],
    topic_centroids: dict,
    label: str,
) -> tuple:
    """Build BM25Index and NumpyIndex from the prepared corpus. Returns (bm25, numpy_idx).

    Each index degrades gracefully on failure: BM25 failure disables sparse
    retrieval, NumpyIndex failure disables dense retrieval — neither crashes
    the startup path."""
    all_texts = corpus["all_texts"]
    all_ids = corpus["all_ids"]
    all_topics = corpus["all_topics"]

    bm25 = BM25Index()
    try:
        bm25.build(documents=all_texts, ids=all_ids, topics=all_topics)
        vocab_size = len(bm25._bm25.idf) if bm25._bm25 else 0
        print(f"[{label}] step 5 — BM25 built ({len(all_ids)} docs, {vocab_size} unique tokens)")
    except Exception as exc:
        print(f"[{label}] ERROR: BM25 build failed — sparse retrieval disabled: {exc}")

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

    return bm25, numpy_idx


async def _load_and_index(app: FastAPI, label: str = "startup", include_db: bool = True) -> dict:
    """Orchestrate: load pairs → sync Chroma → build indexes → apply to app.state.
    Returns a summary dict. Called at startup and by /admin/sync-chroma."""
    pairs = await _load_pairs(include_db, label)
    qa_cache["qa_pairs"] = pairs

    topic_counts = Counter(p.get("topic", "unknown") for p in pairs)
    db_sourced = [p for p in pairs if p.get("source") == "db-post"]
    print(f"[{label}] topics in corpus: {dict(sorted(topic_counts.items()))}")
    print(f"[{label}] DB-sourced pairs: {len(db_sourced)}")

    corpus = _prepare_corpus(pairs, label)
    all_embeddings, topic_centroids = await _fetch_embeddings(pairs, corpus["all_ids"], label)
    bm25, numpy_idx = _build_indexes(corpus, all_embeddings, topic_centroids, label)

    app.state.bm25 = bm25
    app.state.numpy_index = numpy_idx
    app.state.id_to_text = corpus["id_to_text"]
    app.state.id_to_topic = corpus["id_to_topic"]
    app.state.centroids = topic_centroids
    app.state.topic_intro_ids = corpus["topic_intro_ids"]

    return {
        "total_docs": len(pairs),
        "db_docs": len(db_sourced),
        "seed_docs": len(pairs) - len(db_sourced),
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


@app.post("/admin/sync-chroma")
async def admin_sync_chroma(request: Request, _: None = Depends(require_admin)) -> dict:
    """Read all Postgres posts, sync to ChromaDB, rebuild indexes — no restart needed."""
    if _sync_lock.locked():
        return {"status": "already running"}
    async with _sync_lock:
        print("[sync] triggered via /admin/sync-chroma")
        summary = await _load_and_index(request.app, label="sync", include_db=True)
        return {"status": "ok", **summary}


@app.post("/admin/seed-postgres")
async def admin_seed_postgres(body: SeedRequest, _: None = Depends(require_admin)) -> dict:
    """Insert fake test users/subjects/posts/comments into Postgres.
    Does NOT touch ChromaDB — call /admin/sync-chroma afterwards.
    Safe to call multiple times (idempotent). Pass {"clean": true} to wipe and re-insert."""
    if not DB_URL:
        raise HTTPException(status_code=503, detail="DATABASE_URL not set — cannot seed")

    print(f"[seed] connecting to Postgres (clean={body.clean})")
    try:
        conn = await asyncpg.connect(DB_URL, timeout=10.0)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Postgres: {exc}")

    try:
        await ensure_users(conn)
        subject_map = await ensure_subjects(conn)
        if body.clean:
            await clean_posts(conn)
        inserted, skipped = await insert_posts(conn, subject_map)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        await conn.close()

    print(f"[seed] done — inserted={inserted} skipped={skipped}")
    return {"status": "ok", "inserted": inserted, "skipped": skipped}


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
