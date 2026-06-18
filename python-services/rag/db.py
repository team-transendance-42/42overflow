"""
Reads Post + Comment rows from PostgreSQL and maps them to the RAG pair format.
Returns an empty list (never crashes) if the DB is unreachable or tables don't
exist — the service falls back to seed-only mode gracefully.

Only posts that have at least one non-deleted top-level comment are returned.
A post with no answer has no knowledge to offer the LLM.
"""

from config import DB_URL
import asyncpg


def _normalize_topic(title: str) -> str:
    """Lower-case and hyphenate a project name for use as RAG topic/tag.
    'A-Maze-ing' -> 'a-maze-ing', 'Agent Smith' -> 'agent-smith'
    """
    return title.lower().strip().replace(" ", "-")


def _row_to_pair(row) -> dict:
    """Map one asyncpg Row (from the JOIN query) to a RAG pair dict."""
    topic = _normalize_topic(row["project_name"])
    return {
        "id": f"db-post-{row['id']}",
        "question": row["question"],
        "answer": row["answers"] or "",
        "topic": topic,
        "tags": [topic],   # project name as the only tag — improves BM25 keyword matching
        "source": "db-post",
    }


# Fetch all posts that have at least one non-deleted top-level comment.
# JOIN (not LEFT JOIN) — posts with zero qualifying comments are excluded.
# Nested thread replies (parentId IS NOT NULL) excluded to avoid noise.
_QUERY = """
    SELECT
        p.id,
        p.title                                     AS project_name,
        p.content                                   AS question,
        string_agg(
            c.content,
            E'\\n\\n'
            ORDER BY c.created_at ASC
        ) FILTER (
            WHERE c.deleted_at IS NULL
              AND c."parentId" IS NULL    -- nested thread replies excluded to avoid noise
        )                                           AS answers
    FROM "Post" p
    JOIN "Comment" c
        ON  c."postId"   = p.id
        AND c.deleted_at IS NULL
        AND c."parentId" IS NULL          -- nested thread replies excluded to avoid noise
    WHERE p.deleted_at IS NULL
      AND p.content     IS NOT NULL
      AND p.content     <> ''
    GROUP BY p.id, p.title, p.content
"""

_TABLES_READY_QUERY = """
    SELECT COUNT(*) FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN ('Post', 'Comment')
"""


async def load_db_pairs() -> list[dict]:
    # Mask password in logs: show only the host/db part
    safe_url = DB_URL.split("@")[-1] if DB_URL and "@" in DB_URL else DB_URL or "(not set)"
    print(f"[db] connecting to: {safe_url}")

    if not DB_URL:
        print("[db] DB_URL not set — skipping DB sync")
        return []

    try:
        conn = await asyncpg.connect(DB_URL)
        print("[db] connected to Postgres OK")
    except Exception as exc:
        print(f"[db] could not connect to Postgres: {exc}")
        return []

    try:
        ready = await conn.fetchval(_TABLES_READY_QUERY)
        print(f"[db] Post+Comment tables present: {ready == 2}")
        if ready < 2:
            # Show what tables ARE in the public schema to help diagnose naming issues
            tables = await conn.fetch(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            names = [r["table_name"] for r in tables]
            print(f"[db] tables in public schema: {names}")
            print("[db] Post or Comment table missing — skipping DB sync (schema not migrated yet)")
            return []

        rows = await conn.fetch(_QUERY)
        print(f"[db] fetched {len(rows)} posts with at least one comment")

        pairs = [_row_to_pair(row) for row in rows]

        # Log topic breakdown so we can see what came from DB
        from collections import Counter
        topic_counts = Counter(p["topic"] for p in pairs)
        print(f"[db] loaded {len(pairs)} pairs — topics: {dict(topic_counts)}")

        # Log first 3 questions as a sanity check
        for p in pairs[:3]:
            print(f"[db]   sample: topic={p['topic']!r}  q={p['question'][:70]!r}")


        return pairs

    except Exception as exc:
        print(f"[db] error reading Post+Comment rows: {exc}")
        return []

    finally:
        await conn.close()
        print("[db] connection closed")
