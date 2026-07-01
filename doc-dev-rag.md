# RAG Administration

Replace `<RAG_ADMIN_TOKEN>` with the value of `RAG_ADMIN_TOKEN` from your `.env` file.

---

## 1. Seed PostgreSQL with test data

Populates the PostgreSQL database with fake dev users, subjects, posts, and comments.

**Via HTTP (stack must be up):**

```bash
docker compose exec python-rag curl -X POST \
  http://localhost:8090/admin/seed-postgres \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: Tra-la-la" \
  -d '{}'
```

**Via `dev_populate.py` (from `python-services/rag/`, stack must be up):**

```bash
uv run python dev_populate.py             # insert fake posts into Postgres
uv run python dev_populate.py --clean     # delete fake posts from Postgres (Chroma untouched)
uv run python dev_populate.py --sync-real # rebuild Chroma/numpy/BM25 with real posts only
```

`--clean` and `--sync-real` are mutually exclusive.

---

## 2. Sync PostgreSQL data to ChromaDB

Reads **all** PostgreSQL posts (including any fake/test data), generates embeddings, and stores them in ChromaDB.

```bash
docker compose exec python-rag curl -X POST \
  http://localhost:8090/admin/sync-chroma \
  -H "X-Admin-Token: Tra-la-la"
```

---

## 2b. Sync real posts only (no fake/test data)

Same as above but excludes fake dev users (`dev_populate.py` users). Fake posts stay in Postgres — they are just not indexed in Chroma/numpy/BM25.

```bash
docker compose exec python-rag curl -X POST \
  http://localhost:8090/admin/sync-real \
  -H "X-Admin-Token: Tra-la-la"
```

Or via `dev_populate.py` (requires `RAG_ADMIN_TOKEN` and `RAG_SERVICE_URL` env vars; `RAG_SERVICE_URL` defaults to `http://localhost:8090`):

```bash
# from python-services/rag/
uv run python dev_populate.py --sync-real
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