import asyncio

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, Request

from config import ADMIN_TOKEN, DB_URL
from dev_populate import clean_posts, ensure_subjects, ensure_users, insert_posts
from indexer import load_and_index
from metrics import Metrics
from store import clear_collection

router = APIRouter()
_sync_lock = asyncio.Lock()  # asyncio.Lock: async mutex; `async with _sync_lock` lets only one coroutine enter the block at a time — prevents two concurrent /admin/sync-chroma calls from rebuilding indexes simultaneously


def require_admin(x_admin_token: str | None = Header(None)) -> None:
    """FastAPI dependency — raises 403 if X-Admin-Token header is missing or wrong."""
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")


# docker compose exec python-rag curl -H "X-Admin-Token: $ADMIN_TOKEN" http://localhost:8000/admin/sync-chroma
@router.post("/admin/sync-chroma")
async def admin_sync_chroma(request: Request, _: None = Depends(require_admin)) -> dict:  # Depends(require_admin): FastAPI dependency injection — runs require_admin() before the handler; raises 403 if token is invalid, so the handler body never executes
    """Read all Postgres posts, sync to ChromaDB, rebuild indexes — no restart needed."""
    if _sync_lock.locked():
        return {"status": "already running"}
    async with _sync_lock:
        print("[sync] triggered via /admin/sync-chroma")
        summary = await load_and_index(request.app, label="sync", include_db=True)
        return {"status": "ok", **summary}


# docker compose exec python-rag curl -H "X-Admin-Token: $ADMIN_TOKEN" http://localhost:8000/admin/seed-postgres
@router.post("/admin/seed-postgres")
async def admin_seed_postgres(clean: bool = False, _: None = Depends(require_admin)) -> dict:
    """Insert fake test users/subjects/posts/comments into Postgres.
    Does NOT touch ChromaDB — call /admin/sync-chroma afterwards.
    Safe to call multiple times (idempotent). Pass ?clean=true to wipe and re-insert."""
    if not DB_URL:
        raise HTTPException(status_code=503, detail="DATABASE_URL not set — cannot seed")

    print(f"[seed] connecting to Postgres (clean={clean})")
    try:
        conn = await asyncpg.connect(DB_URL, timeout=10.0)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Postgres: {exc}")

    try:
        await ensure_users(conn)
        subject_map = await ensure_subjects(conn)
        if clean:
            await clean_posts(conn)
        inserted, skipped = await insert_posts(conn, subject_map)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        await conn.close()

    print(f"[seed] done — inserted={inserted} skipped={skipped}")
    return {"status": "ok", "inserted": inserted, "skipped": skipped}


# docker compose exec python-rag curl -H "X-Admin-Token: $ADMIN_TOKEN" http://localhost:8000/admin/wipe
@router.post("/admin/wipe")
async def admin_wipe(request: Request, _: None = Depends(require_admin)) -> dict:
    """Wipe all posts, comments, and subjects from Postgres and all docs from ChromaDB.
    Rebuilds in-memory indexes from seed so the service stays healthy.
    Call /admin/seed-postgres then /admin/sync-chroma to repopulate."""
    if not DB_URL:
        raise HTTPException(status_code=503, detail="DATABASE_URL not set — cannot wipe Postgres")

    try:
        conn = await asyncpg.connect(DB_URL, timeout=10.0)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Postgres: {exc}")

    try:
        comment_count       = await conn.fetchval('SELECT COUNT(*) FROM "Comment"')
        post_count          = await conn.fetchval('SELECT COUNT(*) FROM "Post"')
        subject_count       = await conn.fetchval('SELECT COUNT(*) FROM "Subject"')
        like_count          = await conn.fetchval('SELECT COUNT(*) FROM "Like"')
        membership_count    = await conn.fetchval('SELECT COUNT(*) FROM "SubjectMember"')

        await conn.execute('DELETE FROM "Like"')
        await conn.execute('DELETE FROM "SubjectMember"')
        await conn.execute('DELETE FROM "Comment"')
        await conn.execute('DELETE FROM "Post"')
        await conn.execute('DELETE FROM "Subject"')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        await conn.close()

    try:
        chroma_count = clear_collection()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ChromaDB wipe failed: {exc}")

    print(f"[wipe] deleted {post_count} posts, {comment_count} comments, {subject_count} subjects, {like_count} likes, {membership_count} memberships, {chroma_count} chroma docs")

    summary = await load_and_index(request.app, label="wipe", include_db=False)
    return {
        "status": "ok",
        "deleted": {
            "postgres_likes": like_count,
            "postgres_memberships": membership_count,
            "postgres_comments": comment_count,
            "postgres_posts": post_count,
            "postgres_subjects": subject_count,
            "chroma_docs": chroma_count,
        },
        "indexes_rebuilt_from": "seed",
        **summary,
    }


# docker compose exec python-rag curl -H "X-Admin-Token: $ADMIN_TOKEN" http://localhost:8000/admin/metrics
@router.get("/admin/metrics")
def metrics_endpoint(request: Request, _: None = Depends(require_admin)) -> dict:
    m: Metrics = request.app.state.metrics
    return {
        "uptime_seconds": m.uptime_seconds(),
        "corpus_size": m.corpus_size,
        "last_sync_at": m.last_sync_at,
        "retrieve_total": m.retrieve_total,
        "retrieve_errors": m.retrieve_errors,
        "bm25_only_fallbacks": m.bm25_only_fallbacks,
    }
