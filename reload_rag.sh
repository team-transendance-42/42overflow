#!/bin/bash
# Reload the RAG service from Postgres. Run from the project root.
# Token is from llm-system-interface/.env — hardcoded below to avoid shell expansion issues.(replace with current one)
# See docdev.md "RAG — Sync & Populate" for full instructions.

docker compose exec python-rag curl -s -X POST \
  http://localhost:8090/admin/reload-from-db \
  -H "X-Admin-Token: traLala-naRozden&Den&Ela!"
