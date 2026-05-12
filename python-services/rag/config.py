# rag/config.py
# Single place for all configuration. Reads from environment variables
# so the same code works locally (localhost) and in Docker (service names).
#
# os.getenv(name, default) — reads the env var named `name`.
# If it's not set, uses `default`. So you can run `python3 testing.py`
# without sourcing .env and get sensible localhost defaults.
#
# To use custom values: `source .env && python3 testing.py`
# Or set manually:      `export OLLAMA_URL=http://localhost:11434`

import os

OLLAMA_URL  = os.getenv("OLLAMA_URL",  "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL   = os.getenv("LLM_MODEL",   "gemma3:4b") # "gemma4:e4b"
CHROMA_URL  = os.getenv("CHROMA_URL",  "http://localhost:8000")
DB_URL      = os.getenv("DATABASE_URL", "") # todo: use a real DB URL in prod, empty string disables DB sync and falls back to seed-only mode
