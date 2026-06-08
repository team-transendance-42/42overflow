the minimum stack: 
	a vector store (ChromaDB)
	a model server (Ollama)
	the app layer that talks to them
===============================

docker-compose.yml starts ollama, chromadb, and python-rag, and the Python service only needs FastAPI plus HTTP client code.
===============================

For a basic RAG setup, you need a vector database and an LLM server, not a regular SQL database.

the pieces are wired in docker-compose.yml, llm-system-interface/rag/python-service/main.py, and llm-system-interface/services/rag.go.
===============================

Ollama for chat and embeddings
ChromaDB for vector storage
PostgreSQL only for the main app data, not for the RAG test itself

The repo already defaults to gemma4:4b for chat and nomic-embed-text for embeddings in llm-system-interface/.env. One detail: the init container pulls the chat model, but you may still need to pull the embedding model once.
=========================

docker compose up -d ollama chromadb python-rag llm-server
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec llm-server curl -fsS http://localhost:8081/healthz
---

Then index one document and ask one question:
docker compose exec llm-server curl -sS -X POST http://localhost:8081/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{"collection":"demo","documents":["Paris is the capital of France.","Berlin is the capital of Germany."]}'

docker compose exec llm-server curl -sS -X POST http://localhost:8081/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"collection":"demo","question":"What is the capital of France?","top_k":3}'
---

Expected result: the first call stores the documents in Chroma, and the second call returns an answer plus the retrieved contexts.

If you want, I can give you step 2 next: a super small chunking/indexing script so you can feed a text file into RAG instead of hardcoded strings.