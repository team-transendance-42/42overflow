# Single place for all configuration. Reads from environment variables
# so the same code works locally (localhost) and in Docker (service names).
#
# os.getenv(name, default) — reads the env var named `name`.
# If it's not set, uses `default`. So you can run `python3 testing.py`
# without sourcing .env and get sensible localhost defaults.

import os

CHROMA_URL = os.getenv("CHROMA_URL", "http://localhost:8000")
# BAAI/bge-small-en-v1.5 = 384-dim, ~100 MB RAM — default for memory-constrained machines.
# nomic-ai/nomic-embed-text-v1.5 = 768-dim, ~2 GB RAM — currently used.
# Changing this requires wiping the ChromaDB volume (different dimensions are incompatible).
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
# todo: use a real DB URL in prod, empty string disables DB sync and falls back to seed-only mode
DB_URL = os.getenv("DATABASE_URL", "")
# Secret token required in X-Admin-Token header to call /admin/* endpoints.
# If not set, admin endpoints are disabled (return 403).
ADMIN_TOKEN = os.getenv("RAG_ADMIN_TOKEN", "")
