 // replace <RAG_ADMIN_TOKEN> with the value of <RAG_ADMIN_TOKEN> in .env file
 
 // populate postgres db with test data: users, subjects, posts, comments: all needed for the rag testing
ddocker compose exec python-rag curl -X POST \
    http://localhost:8090/admin/seed-postgres \
    -H 'Content-Type: application/json' \
    -H 'X-Admin-Token: Tra-la-la' \
    -d '{}'

// take relevant info from postgres db and embed and store in chromadb
docker compose exec python-rag curl -X POST \
    http://localhost:8090/admin/sync-chroma \
    -H 'X-Admin-Token: Tra-la-la'

// delete info from postgres(subjects, posts, comments)
docker compose exec python-rag curl -X POST http://localhost:8090/admin/wipe -H "X-Admin-Token: Tra-la-la"

// check index readiness — used by docker-compose healthcheck and the Go service;
// returns: status, qa_count (QA pairs loaded), embeddings_ready (NumpyIndex matrix built), bm25_ready (BM25 index built)
//Unauthenticated /healthz is industry standard — Kubernetes, Docker,
  AWS ALB, and virtually every load balancer hit health endpoints
  without auth. Requiring a token would break those integrations.
  docker compose exec python-rag curl -s http://localhost:8090/healthz | python3 -m json.tool

// check admin metrics — used by the Go service to determine if the RAG service is ready to serve requests
  docker compose exec python-rag curl -s http://localhost:8090/admin/metrics -H "X-Admin-Token: Tra-la-la"

// watch logs in real time — useful for debugging RAG service issues
  docker compose logs -f python-rag

====================
clear and restart chromadb:

  docker compose exec 0.chromadb /bin/sh -c "rm -rf /chroma/chroma/*"
  docker compose restart chromadb
  docker compose exec python-rag curl -s -H "X-Admin-Token: Tra-la-la" \
    -X POST http://localhost:8090/admin/sync-chroma | python3 -m json.tool




