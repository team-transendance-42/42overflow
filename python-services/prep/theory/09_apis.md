 Service: Go :8081
  Method: GET
  Path: /healthz
  What it does: health check
  ────────────────────────────────────────
  Service: Go :8081
  Method: POST
  Path: /api/ai-assist
  What it does: streams Gemini response as SSE
  ────────────────────────────────────────
  Service: Go :8081
  Method: POST
  Path: /api/ollama
  What it does: streams Ollama response as SSE (1 concurrent max)




   Service: Go :8081
  Method: ~~POST~~
  Path: ~~`/api/rag/index`~~
  What it does: commented out

 Service: Go :8081
  Method: ~~POST~~
  Path: ~~`/api/rag/ask`~~
  What it does: commented out




 ────────────────────────────────────────
  Service: Python RAG :8090
  Method: GET
  Path: /healthz
  What it does: {"status":"ok","qa_count":N}
  ────────────────────────────────────────
  Service: Python RAG :8090
  Method: POST
  Path: /rag/retrieve
  What it does: hybrid search only → returns contexts + confidence, no
    LLM
  ────────────────────────────────────────
  Service: Python RAG :8090
  Method: POST
  Path: /rag/ask
  What it does: full pipeline → retrieve + generate → answer + contexts
  ────────────────────────────────────────
  Service: Python STT :8091
  Method: GET
  Path: /healthz
  What it does: health check
  ────────────────────────────────────────
  Service: Python STT :8091
  Method: POST
  Path: /convert_audio
  What it does: multipart audio upload → Whisper transcript


  ============================================
  OUTBOUND CALLS (WHAT EACH SERVICE CALLS)
  ============================================

  
  Go → external

  To: Gemini
  Method + URL: POST $GEMINI_URL
  Why: stream LLM response for /api/ai-assist
  ────────────────────────────────────────
  To: Ollama
  Method + URL: POST $OLLAMA_URL/api/chat
  Why: stream LLM for /api/ollama and RAG answer
  ────────────────────────────────────────
  To: Ollama
  Method + URL: POST $OLLAMA_URL/api/embed
  Why: embed texts for RAG indexing (Go-side RAG)
  ────────────────────────────────────────
  To: ChromaDB
  Method + URL: POST $CHROMA_URL/api/v1/collections
  Why: create collection
  ────────────────────────────────────────
  To: ChromaDB
  Method + URL: POST $CHROMA_URL/api/v1/collections/{id}/upsert
  Why: store embeddings
  ────────────────────────────────────────
  To: ChromaDB
  Method + URL: POST $CHROMA_URL/api/v1/collections/{id}/query
  Why: dense retrieval
  ────────────────────────────────────────



  To: Python RAG
  Method + URL: POST $PY_RAG_URL/rag/index
  Why: delegate indexing to Python (conditional)
  ────────────────────────────────────────
  To: Python RAG
  Method + URL: POST $PY_RAG_URL/rag/ask
  Why: delegate full RAG to Python (conditional)


  ====================
   Python RAG → external

  To: Ollama
  Method + URL: POST $OLLAMA_URL/api/embed
  Why: embed query at search time (embedder.py)
  ────────────────────────────────────────
  To: Ollama
  Method + URL: POST $OLLAMA_URL/api/chat
  Why: generate answer (generator.py, 300s timeout)
  ────────────────────────────────────────
  To: ChromaDB
  Method + URL: SDK calls → /api/v1/...
  Why: upsert at startup, query at search time (store.py)
  ────────────────────────────────────────
  To: PostgreSQL
  Method + URL: asyncpg TCP
  Why: load QA pairs from DB at startup (db.py)
  




