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
    if not DB_URL:
        print("[db] DB_URL not set — skipping DB sync")
        return []

    try:
        conn = await asyncpg.connect(DB_URL)  # asyncpg= async Postgres
    except Exception as exc:
        print(f"[db] could not connect to Postgres: {exc}")
        return []

    try:
        exists = await conn.fetchval(_TABLE_EXISTS_QUERY)
        if not exists:
            print("[db] QAPair table not found — skipping DB sync (schema not migrated yet)")
            return []

        rows = await conn.fetch(_QUERY)
        pairs = [
            {
                "id": f"db-{row['id']}",    # prefix avoids collision with seed IDs
                "question": row["question"],
                "answer": row["answer"],
                "topic": row["topic"],
                "tags": list(row["tags"] or []),
                "source": row["source"] or "db",
            }
            for row in rows
        ]
        print(f"[db] loaded {len(pairs)} Q&A pairs from Postgres")
        return pairs

    except Exception as exc:
        print(f"[db] error reading QAPair rows: {exc}")
        return []

    finally:
        await conn.close()
