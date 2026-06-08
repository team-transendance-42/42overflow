  The full request path for /api/community:

  Browser
    → POST /api/community (Go)
      → ollamaQueue semaphore (blocks if another Ollama req in flight)
      → StreamRagAnswer()
        → doJSON POST /rag/retrieve (Python, no timeout)
            → hybrid_search()
                → embed_texts([question])  ← POST Ollama /api/embed
  (nomic-embed-text)
                → query_dense()            ← ChromaDB vector search
                → bm25_index.search()      ← in-memory, instant
                → RRF merge
        → build strict RAG prompt (~300-600 tokens of context)
        → withRetry → POST Ollama /api/chat (gemma3:4b, streaming)
            → tokens stream back through Go → SSE to browser

  Every single step is sequential. No parallelism anywhere.
