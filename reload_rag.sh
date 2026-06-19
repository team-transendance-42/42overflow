#!/bin/bash
# Sync RAG with Postgres + ChromaDB. Run from the project root.
# Requires the stack to be up (docker compose up).
#
# Token is read from python-services/rag/.env — set RAG_ADMIN_TOKEN there.
# The /admin/reload-from-db endpoint in python-rag validates the token.

set -euo pipefail

ENV_FILE="python-services/rag/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found. Copy .env.example and fill in values."
  exit 1
fi

TOKEN=$(grep -E '^RAG_ADMIN_TOKEN=' "$ENV_FILE" | cut -d= -f2-)

if [[ -z "$TOKEN" ]]; then
  echo "ERROR: RAG_ADMIN_TOKEN not set in $ENV_FILE"
  exit 1
fi

echo "Reloading RAG from Postgres..."
docker compose exec python-rag curl -sf -X POST \
  http://localhost:8090/admin/reload-from-db \
  -H "X-Admin-Token: $TOKEN"
echo
