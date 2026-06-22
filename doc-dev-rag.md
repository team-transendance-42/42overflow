 // replace <RAG_ADMIN_TOKEN> with the value of RAG_ADMIN_TOKEN in .env file
 
 docker compose exec python-rag curl -s -X POST \
    http://localhost:8090/admin/seed-postgres \
    -H 'Content-Type: application/json' \
    -H 'X-Admin-Token: <RAG_ADMIN_TOKEN>' \
    -d '{}'

  docker compose exec python-rag curl -s -X POST \
    http://localhost:8090/admin/sync-chroma \
    -H 'X-Admin-Token: <RAG_ADMIN_TOKEN>'