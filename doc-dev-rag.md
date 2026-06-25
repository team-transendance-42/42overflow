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
  docker compose exec python-rag curl -X POST http://localhost:8090/admin/wipe -H "X-Admin-Token: Tra-la-la"

//	smoke-test once Docker is running:
  docker compose exec python-rag curl -s http://localhost:8090/admin/metrics -H "X-Admin-Token: Tra-la-la" | python3 -m json.tool
bm25_only_fallbacks: 7 -> means the embedding model failed 7 times at query time — has_embeddings was False, meaning NumpyIndex returned no results
  (or the embed call threw), so retrieval fell back to keyword search (BM25) alone, with no dense/semantic component.
debug:
docker compose logs python-rag | grep "embedding failed\|dense search failed"
or
docker compose logs python-rag | grep -E "\[startup\]|\[indexer\]|numpy|indexed"


  docker compose logs -f python-rag

  How does poll() work and why is non-blocking I/O required for webserv?
====================
clear and restart chromadb:

  docker compose exec chromadb /bin/sh -c "rm -rf /chroma/chroma/*"
  docker compose restart chromadb
  docker compose exec python-rag curl -s -H "X-Admin-Token: Tra-la-la" \
    -X POST http://localhost:8090/admin/sync-chroma | python3 -m json.tool




