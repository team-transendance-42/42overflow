"""
Reads Post + Comment rows from PostgreSQL and maps them to the RAG pair format.
Returns an empty list (never crashes) if the DB is unreachable or tables don't
exist — the service falls back to seed-only mode gracefully.

Only posts that have at least one non-deleted top-level comment are returned.
A post with no answer has no knowledge to offer the LLM.
"""

from config import DB_URL
import asyncpg
from asyncpg import Record # a high-performance PostgreSQL client library for Python, built specifically for use with asyncio (Python's async/await framework)


def _normalize_topic(title: str) -> str:
    """Lower-case and hyphenate a project name for use as RAG topic/tag.
    'A-Maze-ing' -> 'a-maze-ing', 'Agent Smith' -> 'agent-smith'
    """
    return title.lower().strip().replace(" ", "-")


def _row_to_pair(row: Record) -> dict: # exact, documents what actually gets passed in.
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
# Subject JOIN provides the canonical slug used as topic/tag.
# || concat symbol is used to combine title + content into a single question string.
# str_agg() turn many rows into one string
_QUERY = """
    SELECT
        p.id,
        s.slug                                              AS project_name,
        p.title || E'\\n\\n' || p.content                  AS question,
        string_agg(
            c.content,
            E'\\n\\n'
            ORDER BY c.created_at ASC
        ) FILTER (
            WHERE c.deleted_at IS NULL
              AND c."parentId" IS NULL
        )                                                   AS answers
    FROM "Post" p
    JOIN "Subject" s ON s.id = p."subjectId"
    JOIN "Comment" c
        ON  c."postId"   = p.id
        AND c.deleted_at IS NULL
        AND c."parentId" IS NULL
    WHERE p.deleted_at IS NULL
      AND p.content     IS NOT NULL
      AND p.content     <> ''
    GROUP BY p.id, s.slug, p.title, p.content
"""

_TABLES_READY_QUERY = """
    SELECT COUNT(*) FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN ('Post', 'Comment', 'Subject')
"""


async def load_db_pairs() -> list[dict]:
    # Mask password in logs: show only the host/db part
    safe_url = DB_URL.split("@")[-1] if DB_URL and "@" in DB_URL else DB_URL or "(not set)"
    print(f"[db] connecting to: {safe_url}")

    if not DB_URL:
        print("[db] DB_URL not set — skipping DB sync")
        return []

    try:
        conn = await asyncpg.connect(DB_URL, timeout=10.0)
        print("[db] connected to Postgres OK")
    except Exception as exc:
        print(f"[db] could not connect to Postgres: {exc}")
        return []

    try:
        ready = await conn.fetchval(_TABLES_READY_QUERY)
        print(f"[db] Post+Comment+Subject tables present: {ready == 3}")
        if ready < 3:
            # Show what tables ARE in the public schema to help diagnose naming issues
            tables = await conn.fetch(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            names = [r["table_name"] for r in tables]
            print(f"[db] tables in public schema: {names}")
            print("[db] Post, Comment, or Subject table missing — skipping DB sync (schema not migrated yet)")
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
