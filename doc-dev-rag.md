 // replace <RAG_ADMIN_TOKEN> with the value of RAG_ADMIN_TOKEN in .env file
 
 // populate postgres db with test data: users, subjects, posts, comments: all needed for the rag testing
docker compose exec python-rag curl -s -X POST \
    http://localhost:8090/admin/seed-postgres \
    -H 'Content-Type: application/json' \
    -H 'X-Admin-Token: Tra-la-la' \
    -d '{}'

// take relevant info from postgres db and embed and store in chromadb
docker compose exec python-rag curl -s -X POST \
    http://localhost:8090/admin/sync-chroma \
    -H 'X-Admin-Token: Tra-la-la'

// delete info from postgres(subjects, posts, comments)
  curl -X POST http://localhost:8090/admin/wipe -H "X-Admin-Token: Tra-la-la"

//	smoke-test once Docker is running:
  docker compose exec python-rag curl -s http://localhost:8090/metrics | python3 -m json.tool

  docker compose logs -f python-rag


