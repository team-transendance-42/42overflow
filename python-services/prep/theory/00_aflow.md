
  Browser
    │ POST /api/community {"prompt": "what is malloc?"}
    ▼
  Caddy → SvelteKit (adds auth headers)
    ▼
  Go llm-server :8081
    ├─ semaphore (1 at a time)
    ├─ Go RAM cache? → HIT: return instantly
    │                → MISS: continue ↓
    ▼
  Python-rag :8090  POST /rag/retrieve
    ├─ embed question (fastembed, ~100ms or 0ms if LRU hit)
    ├─ detect topic (numpy centroid dot product, ~0.01ms)
    ├─ NumpyIndex dense search (matrix multiply, ~0.05ms)
    ├─ BM25 sparse search (inverted index, ~1ms)
    ├─ RRF merge → top 4 docs
    └─ return {contexts, confidence}
    ▼
  Go: confidence < 0.02? → return "no context" (skip Ollama)
  Go: build prompt (extractAnswer strips Q: prefix)
    ▼
  Ollama :11434  POST /api/chat  stream=true
    └─ Gemma 4B generates tokens one by one
    ▼
  Go: token → rawCh → goroutine → outCh → streamSSE → SSE to browser
                                          ↓
                                 if stream complete: Go RAM cache write