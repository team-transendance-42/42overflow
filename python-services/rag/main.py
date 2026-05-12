from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import load_db_pairs
from embedder import embed_texts, format_doc, make_doc_hash, make_doc_id
from seed import load_seed
from store import ensure_collection, get_existing_hashes, upsert

# State shared across requests — populated at startup
state: dict = {"qa_pairs": []}


def _merge(seed_pairs: list[dict], db_pairs: list[dict]) -> list[dict]:
    """Seed is the baseline. DB pairs are additive; DB wins on duplicate questions."""
    merged: dict[str, dict] = {key["question"]: key for key in seed_pairs} # merged = { q: {question, answer, ...} } for all seed pairs

    for p in db_pairs:
        merged[p["question"]] = p  # DB overwrites seed if same question
    return list(merged.values())


async def _sync_to_chroma(pairs: list[dict]) -> None:
    for p in pairs:
        p["_id"]   = make_doc_id(p["question"])
        p["_hash"] = make_doc_hash(p["question"], p["answer"])
        p["_text"] = format_doc(p["question"], p["answer"])

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
--------------------------------
• Tdecorator from contextlib for writing async context managers.
• Lets you manage setup and cleanup logic for resources (e.g., DB connections, caches) asynchronously.
• Code before 'yield' runs at startup (setup), code after 'yield' runs at shutdown (cleanup).
• Used by FastAPI for lifespan events (app startup/shutdown).

@asynccontextmanager
This is a special label that tells Python, “The next function will help set things up and clean up when the app starts and stops.”
Example:
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # Setup code here
    yield
    # Cleanup code here

app = FastAPI(lifespan=lifespan)
--------------------------------
"""
@asynccontextmanager
async def lifespan(app: FastAPI): # will run when the app starts and stops.
    # Step 1: always load seed
    seed_pairs = load_seed()
    print(f"[startup] step 1 — {len(seed_pairs)} pairs from seed.json")

    # Step 2: try DB, merge
    db_pairs = await load_db_pairs()
    state["qa_pairs"] = _merge(seed_pairs, db_pairs)
    print(f"[startup] step 2 — {len(state['qa_pairs'])} pairs total after merge")

    # Step 3: smart sync to ChromaDB
    await _sync_to_chroma(state["qa_pairs"])
    print("[startup] step 3 — ChromaDB sync complete")

    # Step 4 (BM25 index) will be added here

    yield # app runs and answers questions for users.

    state["qa_pairs"] = [] # when app shutdown, clear the state to free memory:needed if used not in a docker container, but in a serverless environment like AWS Lambda where the same instance may be reused for multiple requests. Clearing the state on shutdown helps prevent data leakage between requests and ensures that each request starts with a clean slate.


app = FastAPI(lifespan=lifespan) #  use the lifespan func for start and shuttdown the app.


@app.get("/healthz")
def healthz():
    return {"status": "ok", "qa_count": len(state["qa_pairs"])}
