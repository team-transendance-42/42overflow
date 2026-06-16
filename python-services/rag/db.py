"""
Reads QAPair rows from PostgreSQL.
Returns an empty list (never crashes) if the DB is unreachable or the table
doesn't exist yet — the service falls back to seed-only mode gracefully.
"""

from config import DB_URL
import asyncpg  # async Postgres client library — more modern than psycopg, works well with FastAPI
"""
Allows Python code to connect to, query, and interact with a PostgreSQL database
using async/await syntax. Enables non-blocking database operations, which is
important for high-performance web servers and APIs.
"""


# Expected columns in the QAPair table.
# Matches the Prisma model proposed in the design.
_QUERY = """
    SELECT id, question, answer, topic, tags, source
    FROM "QAPair"
    ORDER BY id
"""

_TABLE_EXISTS_QUERY = """
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'QAPair'
    )
"""

# todo: need to adjust values: what are the real fields and real table name etc


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
        exists = await conn.fetchval(_TABLE_EXISTS_QUERY)
        print(f'[db] QAPair table exists: {exists}')
        if not exists:
            # Show what tables ARE in the public schema to help diagnose naming issues
            tables = await conn.fetch(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            names = [r["table_name"] for r in tables]
            print(f"[db] tables in public schema: {names}")
            print("[db] QAPair table not found — skipping DB sync (schema not migrated yet)")
            return []

        rows = await conn.fetch(_QUERY)
        print(f"[db] fetched {len(rows)} rows from QAPair")

        pairs = [
            {
                "id": f"db-{row['id']}",
                "question": row["question"],
                "answer": row["answer"],
                "topic": row["topic"],
                "tags": list(row["tags"] or []),
                "source": row["source"] or "db",
            }
            for row in rows
        ]

        # Log topic breakdown so we can see what came from DB
        from collections import Counter
        topic_counts = Counter(p["topic"] for p in pairs)
        print(f"[db] loaded {len(pairs)} pairs — topics: {dict(topic_counts)}")

        # Log first 3 questions as a sanity check
        for p in pairs[:3]:
            print(f"[db]   sample: topic={p['topic']!r}  q={p['question'][:70]!r}")

        return pairs

    except Exception as exc:
        print(f"[db] error reading QAPair rows: {exc}")
        return []

    finally:
        await conn.close()
        print("[db] connection closed")
