Pros of DB integration:
  - Add/update QA pairs without touching JSON files or redeploying
  - Can track who added what (source, createdAt)
  - Scales — 10k rows is trivial for Postgres
  - DB wins on duplicate questions (from _merge()) — good for corrections

  Cons / risks:
  - python-rag only syncs DB at startup, not live. Adding DB rows requires docker compose restart python-rag
  (~2min restart due to embedding)
  - prisma db push --accept-data-loss in the app's startup command will DROP columns not in schema — safe after
  you add QAPair, but be careful with future schema changes
  - If DATABASE_URL is wrong or DB is down, db.py returns [] silently — seed-only mode, no crash, but easy to
  miss during testing
  - tags in Postgres is String[] (text array) — asyncpg returns it as a Python list, which maps correctly
