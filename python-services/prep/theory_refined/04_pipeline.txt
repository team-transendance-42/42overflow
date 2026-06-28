
  STARTUP
  seed.json ──┐
              ├─→ format_doc() → embed() → ChromaDB (persist)
  Postgres ───┘                          ↓
                                get_embeddings() ← pull back
                                         ↓
                              build_topic_centroids()
                              NumpyIndex.build()
                              BM25Index.build()

  QUERY
  question ──→ embed() ──→ detect_topic() (centroid)
                     │              │
                     │         "norminette" (confident)
                     ↓              ↓
              NumpyIndex.search(filter=norminette)
              BM25Index.search(filter=norminette)
                           ↓
                        RRF merge
                           ↓
                      top-4 docs → Go → Ollama → user