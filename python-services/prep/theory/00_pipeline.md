 User question
       │
       ▼
    Embedder  ────────────────────────────────┐
    (fastembed, nomic-embed-text-v1.5)        │
       │ 768-dim vector                       │
       ▼                                      ▼
   detect_topic()           ┌────────────────────────────────┐
   (centroid similarity)    │  Hybrid Retrieval               │
       │                    │  ┌──────────┐  ┌────────────┐  │
       │ topic or None       │  │NumpyIndex│  │ BM25Index  │  │
       └──────────────────► │  │(dense)   │  │(sparse)    │  │
                            │  └──────────┘  └────────────┘  │
                            │        │               │        │
                            │        └───── RRF ─────┘        │
                            └────────────────────────────────┘
                                         │ top-k docs
                                         ▼
                                 generator.py
                                (Ollama / LLM)
                                         │
                                         ▼
                                    Answer text