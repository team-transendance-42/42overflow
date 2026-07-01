from collections import Counter
import time

from fastapi import FastAPI

from bm25_index import BM25Index
from db import load_db_pairs
from detector import build_topic_centroids
from embedder import embed_texts, format_doc, make_doc_hash
from numpy_index import NumpyIndex
from seed import load_seed
from store import get_embeddings, get_existing_hashes, upsert



async def _sync_to_chroma(pairs: list[dict]) -> dict[str, list[float]]:
    """Sync question-answer pairs to ChromaDB — only embeds new or changed docs.
    Returns {doc_id: embedding} for every doc that was freshly embedded this
    call. Empty dict when nothing changed or embedding failed. The caller uses
    this to avoid a redundant GET for docs whose vectors are already in memory."""
    augmented = [
        {
            **p,
            "_id":   make_doc_hash(p["question"], p["answer"]),
            "_hash": make_doc_hash(p["question"], p["answer"]),
            "_text": format_doc(p["question"], p["answer"], p.get("tags", [])),
        }
        for p in pairs
    ]
    try:
        existing = get_existing_hashes([p["_id"] for p in augmented])
    except Exception as exc:
        print(f"[chroma] WARNING: get_existing_hashes failed, re-embedding all {len(augmented)} docs: {exc}")
        existing = {}

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

    Doing this in one loop avoids calling format_doc and make_doc_hash twice per
    pair.
    Returns a dict with: all_texts, all_ids, all_topics, topic_intro_ids,
    id_to_text, id_to_topic."""
    all_texts: list[str] = []
    all_ids: list[str] = []
    all_topics: list[str] = []
    topic_intro_ids: dict[str, str] = {}

    for p in pairs:
        text = format_doc(p["question"], p["answer"], p.get("tags", []))
        doc_id = make_doc_hash(p["question"], p["answer"])
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


async def load_and_index(app: FastAPI, label: str = "startup", include_db: bool = True) -> dict:
    """Orchestrate: load pairs → sync Chroma → build indexes → apply to app.state.
    Returns a summary dict. Called at startup and by /admin/sync-chroma."""
    pairs = await _load_pairs(include_db, label)
    app.state.qa_pairs = pairs

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

    if hasattr(app.state, "metrics"):
        app.state.metrics.corpus_size = len(pairs)
        app.state.metrics.last_sync_at = time.time()

    return {
        "total_docs": len(pairs),
        "db_docs": len(db_sourced),
        "seed_docs": len(pairs) - len(db_sourced),
        "topics": dict(sorted(topic_counts.items())),
        "embeddings_ready": bool(all_embeddings),
    }
