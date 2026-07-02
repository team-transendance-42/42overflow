#!/bin/bash
# Step 1: Add test users, subjects, posts, comments to persistent volume postgres.
# Step 2: Add the data from step 1 to chromadb for rag ai service(synch chromadb with postgres)
# Run from the project root.
# Reads RAG_ADMIN_TOKEN from the environment — set it from llm-system-interface/.env before running:
#   export RAG_ADMIN_TOKEN=<value from .env>
# See doc-dev-rag.md for manual runs, including delete test data

if [ -z "${RAG_ADMIN_TOKEN}" ]; then
    RAG_ADMIN_TOKEN=$(grep '^RAG_ADMIN_TOKEN=' llm-system-interface/.env | cut -d '=' -f2-)
fi

if [ -z "${RAG_ADMIN_TOKEN}" ]; then
    echo "ERROR: RAG_ADMIN_TOKEN not found in environment or llm-system-interface/.env" >&2
    exit 1
fi

if [ -z "${LLM_INTERNAL_SECRET}" ]; then
    LLM_INTERNAL_SECRET=$(grep '^LLM_INTERNAL_SECRET=' llm-system-interface/.env | cut -d '=' -f2-)
fi

if [ -z "${LLM_INTERNAL_SECRET}" ]; then
    echo "ERROR: LLM_INTERNAL_SECRET not found in environment or llm-system-interface/.env" >&2
    exit 1
fi

echo "==== step 1: seed-postgres ========"
docker compose exec -T python-rag curl -X POST \
    http://localhost:8090/admin/seed-postgres \
    -H 'Content-Type: application/json' \
    -H "X-Admin-Token: ${RAG_ADMIN_TOKEN}" \
    -d '{}'
echo ""

echo "==== step 2: sync-chroma ========"
docker compose exec -T python-rag curl -X POST \
    http://localhost:8090/admin/sync-chroma \
    -H "X-Admin-Token: ${RAG_ADMIN_TOKEN}"
echo ""

echo "==== step 3: clear go rag cache ========"
docker compose exec -T python-rag curl -X POST \
    http://llm-server:8081/admin/clear-rag-cache \
    -H "X-Internal-Secret: ${LLM_INTERNAL_SECRET}"
echo ""
