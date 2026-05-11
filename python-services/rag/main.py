from contextlib import asynccontextmanager
from fastapi import FastAPI
from db import load_db_pairs
from seed import load_seed

# State shared across requests — populated at startup
state: dict = {"qa_pairs": []}


def _merge(seed_pairs: list[dict], db_pairs: list[dict]) -> list[dict]:
    """Seed is the baseline. DB pairs are additive; DB wins on duplicate questions."""
    merged: dict[str, dict] = {p["question"]: p for p in seed_pairs}
    for p in db_pairs:
        merged[p["question"]] = p  # DB overwrites seed if same question
    return list(merged.values())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Step 1: always load seed
    seed_pairs = load_seed()
    print(f"[startup] step 1 — {len(seed_pairs)} pairs from seed.json")

    # Step 2: try DB, merge
    db_pairs = await load_db_pairs()
    state["qa_pairs"] = _merge(seed_pairs, db_pairs)
    print(f"[startup] step 2 — {len(state['qa_pairs'])} pairs total after merge")

    # Steps 3-4 (embed + BM25) will be added here incrementally

    yield

    state["qa_pairs"] = []


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "qa_count": len(state["qa_pairs"])}
