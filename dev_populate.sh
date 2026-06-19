#!/bin/bash
# Insert fake posts/comments into Postgres for RAG testing. Run from project root.
# Requires the stack to be up (docker compose up) — connects to Postgres on port 5433.
#
# Usage:
#   bash dev_populate.sh          # insert fake posts (skips existing)
#   bash dev_populate.sh --clean  # wipe fake posts and re-insert fresh

set -euo pipefail

cd python-services/rag
uv run python dev_populate.py "$@"
cd ../..

echo
echo "Next: run 'bash reload_rag.sh' to sync the new posts into ChromaDB."
