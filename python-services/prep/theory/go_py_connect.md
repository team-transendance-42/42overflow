Go server is configured to use Python backend:
docker-compose.yml:43

Go RAG service checks backend and forwards to Python:
rag.go:16
rag.go:160

Go exposes API routes your app calls:
llm_server.go

So the request path is:
Frontend -> llm-server /api/rag/index or /api/rag/ask -> python-rag /rag/index or /rag/ask -> chromadb + ollama.
======
Start stack:
docker compose up --build

Call Go endpoints (Go will route to Python backend):
POST /api/rag/index
POST /api/rag/ask

If you change Python dependencies in pyproject.toml:
Rebuild is required:
docker compose build python-rag
docker compose up -d python-rag

If you only change Python code:
Because main.py is copied at build time, rebuild/restart python-rag to apply changes.