 Browser (Svelte)
     │
     │  POST /api/community { prompt: "..." }
     ▼
  SvelteKit proxy  (passes through to Go)
     │
     │  POST /api/community
     ▼
  Go llm-system-interface (port 8081)
     │  1. Middleware: ErrorRecovery → RateLimiter (burst=2 per IP)
     │  2. Handler:   RagAskStreaming
     │  3. Acquire ollamaQueue semaphore (capacity 1)
     │  4. services.StreamRagAnswer(ctx, question)
     │
     │  POST /rag/retrieve { question: "..." }
     ▼
  Python python-rag (port 8090)        ← FastAPI
     │  1. embed question (fastembed, 768-dim, CPU, cached with LRU)
     │  2. detect topic via centroid similarity
     │  3. NumpyIndex cosine search (in-process, ~0.05ms)
     │  4. BM25 sparse search
     │  5. RRF merge → top-5 context docs
     │
     │  returns: [{ id, text, rrf_score, topic }, ...]
     ▼
  Go (back in StreamRagAnswer)
     │  1. extractAnswer: strip "Q: ..." prefix from each doc
     │  2. build big prompt:
     │        system + contexts [1-5] + "Question: ..."
     │
     │  POST /api/chat { model, messages, stream:true }
     ▼
  Ollama (local, e.g. Gemma 4B)
     │  streams tokens back to Go
     ▼
  Go: goroutine reads tokens → ch <- token
     │
     ▼
  streamSSE: writes "data: token\n\n" and flushes per chunk
     │
     ▼
  Browser receives SSE stream, renders tokens live