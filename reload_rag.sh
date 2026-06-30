#!/bin/bash
# Step 1: Add test users, subjects, posts, comments to persistent volume postgres.
# Step 2: Add the data from step 1 to chromadb for rag ai service(synch chromadb with postgres)
# Run from the project root.
# Token is from llm-system-interface/.env — hardcoded below to avoid shell expansion issues.(replace with the one from .env)
# See docdev.md "RAG — Sync & Populate" for manual runs, including delete test data

echo "==== step 1: seed-postgres ========"
docker compose exec python-rag curl -X POST \
    http://localhost:8090/admin/seed-postgres \
    -H 'Content-Type: application/json' \
    -H 'X-Admin-Token: Tra-la-la' \
    -d '{}'
echo ""

echo "==== step 2: sync-chroma ========"
docker compose exec python-rag curl -X POST \
    http://localhost:8090/admin/sync-chroma \
    -H 'X-Admin-Token: Tra-la-la'
echo ""
