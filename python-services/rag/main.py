from contextlib import asynccontextmanager
from fastapi    import FastAPI

from bm25_index import BM25Index
from db         import load_db_pairs
from embedder   import embed_texts, format_doc, make_doc_hash, make_doc_id
from router     import router as rag_router
from seed       import load_seed
from store      import ensure_collection, get_existing_hashes, upsert

# qa_cache shared across requests — populated at startup
# solid and practical approach for small to medium-scale RAG (Retrieval-Augmented Generation) systems, especially for prototyping or internal tools:
# Strengths:
# Fast in-memory access to QA pairs for quick retrieval.
# Persistent vector storage in ChromaDB for scalable similarity search.
# Clear separation: text data in memory, vectors in a vector DB.
# Easy to extend and debug.

# Limitations for large-scale/production:
# In-memory cache (qa_cache["qa_pairs"]) may not scale for millions of documents or distributed systems.
# No real-time sync between memory and DB if data changes after startup.
# No advanced retrieval (e.g., hybrid search, filtering, sharding).
# Lacks user/session management, security, and distributed cache.
# Best practices for production RAG:

# Use a scalable vector DB (like ChromaDB, Pinecone, Weaviate, etc.) as the single source of truth.
# Implement efficient retrieval pipelines (possibly with hybrid search: vectors + metadata filters).
# Use distributed caching (e.g., Redis) if you need fast access to frequently used data.
# Keep your in-memory cache in sync with DB updates, or use the DB directly for retrieval.
# Add monitoring, logging, and error handling for robustness.
qa_cache: dict = {"qa_pairs": [], "bm25": None}


def _merge(seed_pairs: list[dict], db_pairs: list[dict]) -> list[dict]:
    """Seed is the baseline. DB pairs are additive; DB wins on duplicate questions."""
    try:
        merged: dict[str, dict] = {p["question"]: p for p in seed_pairs}
    except KeyError as exc:
        raise ValueError(f"Seed pair missing 'question' field: {exc}") from exc

    for p in db_pairs:
        try:
            merged[p["question"]] = p
        except KeyError as exc:
            raise ValueError(f"DB pair missing 'question' field: {exc}") from exc
    return list(merged.values())


async def _sync_to_chroma(pairs: list[dict]) -> None:
    ''' Syncs the given question-answer pairs to ChromaDB. generates unique IDs and hashes for each pair and checks which pairs are new or changed compared to existing entries in ChromaDB. Only new or changed pairs are embedded and upserted to ChromaDB, optimizing performance by avoiding unnecessary operations on unchanged data.'''
    for p in pairs:
        p["_id"]   = make_doc_id(p["question"])
        p["_hash"] = make_doc_hash(p["question"], p["answer"])
        p["_text"] = format_doc(p["question"], p["answer"])

    ensure_collection() # has try/catch for connection issues, will raise RuntimeError if ChromaDB is unreachable
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

    embeddings = await embed_texts([p["_text"] for p in to_update])
    upsert(
        ids=[p["_id"] for p in to_update],
        documents=[p["_text"] for p in to_update],
        embeddings=embeddings,
        metadatas=[
            {
                "topic":      p.get("topic", ""),
                "difficulty": p.get("difficulty", ""),
                "doc_hash":   p["_hash"],
            }
            for p in to_update
        ],
    )
    print(f"[chroma] upserted {len(to_update)} docs")


"""
@asynccontextmanager
• decorator from contextlib for writing async context managers.
• Lets you manage setup and cleanup logic for resources (e.g., DB connections, caches) asynchronously.
• Code before 'yield' runs at startup (setup), code after 'yield' runs at shutdown (cleanup).
• Used by FastAPI for lifespan events (app startup/shutdown).
"""
@asynccontextmanager
async def lifespan(app: FastAPI): # will run when the app starts and stops.
    # Step 1: always load seed
    seed_pairs = load_seed()
    print(f"[startup] step 1 — {len(seed_pairs)} pairs from seed.json")

    # Step 2: try DB, merge
    db_pairs = await load_db_pairs()
    qa_cache["qa_pairs"] = _merge(seed_pairs, db_pairs)
    print(f"[startup] step 2 — {len(qa_cache['qa_pairs'])} pairs total after merge")

    # Step 3: ChromaDB + Ollama sync is optional at startup
    try:
        await _sync_to_chroma(qa_cache["qa_pairs"])
        print("[startup] step 3 — ChromaDB sync complete")
    except RuntimeError as exc:
        print(f"[startup] WARNING: ChromaDB sync failed — serving from memory only. Reason: {exc}")

    # Step 4: build BM25 index in RAM from the same texts embedded into ChromaDB.
    # We compute text/id fresh here — cheap string ops, no I/O — so Step 4
    # works correctly even if Step 3 failed (ChromaDB unreachable).
    bm25 = BM25Index()
    bm25.build(
        documents=[format_doc(p["question"], p["answer"]) for p in qa_cache["qa_pairs"]],
        ids=[make_doc_id(p["question"]) for p in qa_cache["qa_pairs"]],
    )
    qa_cache["bm25"] = bm25
    print(f"[startup] step 4 — BM25 index built ({len(qa_cache['qa_pairs'])} docs)")

    # expose indexes to router via app.state (avoids circular imports)
    app.state.bm25       = bm25
    app.state.id_to_text = {
        make_doc_id(p["question"]): format_doc(p["question"], p["answer"])
        for p in qa_cache["qa_pairs"]
    }

    yield # app runs and answers questions for users.

    qa_cache["qa_pairs"] = [] # when app shutdown, clear the qa_cache to free memory:needed if used not in a docker container, but in a serverless environment like AWS Lambda where the same instance may be reused for multiple requests. Clearing the qa_cache on shutdown helps prevent data leakage between requests and ensures that each request starts with a clean slate.

# docker compose logs -f python-rag
app = FastAPI(lifespan=lifespan)
app.include_router(rag_router)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "qa_count": len(qa_cache["qa_pairs"])}
