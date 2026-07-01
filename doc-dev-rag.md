# RAG Administration

Replace `<RAG_ADMIN_TOKEN>` with the value of `RAG_ADMIN_TOKEN` from your `.env` file.

---

## 1. Seed PostgreSQL with test data

Populates the PostgreSQL database with sample:

- Users
- Subjects
- Posts
- Comments

```bash
docker compose exec python-rag curl -X POST \
  http://localhost:8090/admin/seed-postgres \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: Tra-la-la" \
  -d '{}'
```

---

## 2. Sync PostgreSQL data to ChromaDB

Reads the relevant data from PostgreSQL, generates embeddings, and stores them in ChromaDB.

```bash
docker compose exec python-rag curl -X POST \
  http://localhost:8090/admin/sync-chroma \
  -H "X-Admin-Token: Tra-la-la"
```

---

## 3. Wipe PostgreSQL data

Deletes all seeded:

- Subjects
- Posts
- Comments

```bash
docker compose exec python-rag curl -X POST \
  http://localhost:8090/admin/wipe \
  -H "X-Admin-Token: Tra-la-la"
```

---

## 4. Check RAG health

Used by:

- Docker Compose health checks
- Kubernetes
- Load balancers
- The Go service

Returns:

- `status`
- `qa_count`
- `embeddings_ready`
- `bm25_ready`

No authentication is required because health endpoints are intended for infrastructure monitoring.

```bash
docker compose exec python-rag \
  curl -s http://localhost:8090/healthz | python3 -m json.tool
```

---

## 5. Check RAG metrics

Used by the Go service to determine whether the RAG service is ready to serve requests.

```bash
docker compose exec python-rag \
  curl -s http://localhost:8090/admin/metrics \
  -H "X-Admin-Token: Tra-la-la"
```

---

## 6. View RAG logs

Follow the logs in real time.

```bash
docker compose logs -f python-rag
```

---

# Clear and rebuild ChromaDB

## 1. Remove all stored embeddings

```bash
docker compose exec chromadb \
  /bin/sh -c "rm -rf /chroma/chroma/*"
```

## 2. Restart ChromaDB

```bash
docker compose restart chromadb
```

## 3. Rebuild the vector index

```bash
docker compose exec python-rag \
  curl -s \
  -H "X-Admin-Token: Tra-la-la" \
  -X POST http://localhost:8090/admin/sync-chroma \
  | python3 -m json.tool
```