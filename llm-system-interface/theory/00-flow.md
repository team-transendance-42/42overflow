 Browser → SvelteKit (adds X-Internal-Secret, X-User-ID)
    → Go llm-server:8081  [ErrorRecovery → InternalSecret → RateLimiter middleware]
      → handlers/rag.go: acquires ragQueue semaphore (cap=1, 30s timeout)
        → services/rag.go: StreamRagAnswer()
            1. ragCacheGet(question)  → HIT: return cached string over channel
            2. POST python-rag:8090/rag/retrieve  (withRetry, up to 3x)
                Python router.py → retriever.hybrid_search():
                  a. embed_texts([question])   ← fastembed CPU, LRU 512 slots
                  b. detect_topic()            ← cosine vs centroids matrix (numpy, ~0.01ms)
                  c. NumpyIndex.search()       ← in-process cosine (numpy, ~0.05ms)
                  d. BM25Index.search()        ← BM25+, in-memory
                  e. RRF merge (k=60)
                  f. Pin intro doc if detected topic has one
                  g. Return top-4 contexts (id, text, rrf_score)
            3. extractAnswer() strips "Q:..." prefix + "tags:..." suffix per context
            4. buildRAGPrompt() wraps contexts + question
            5. POST ollama:11434/api/chat (streaming, withRetry)
            6. goroutine: readOllamaToChannel → rawCh
            7. goroutine: rawCh → outCh + accumulate → ragCacheSet on close
      → handlers/stream.go: streamSSE() sends each chunk as SSE event
    → Browser renders tokens as they arrive