  ┌──────────────────────────────────────────────────────────────────┐
  │                        docker-compose                            │
  │                                                                  │
  │  ┌──────────┐     ┌────────────┐     ┌────────────────────────┐  │
  │  │ SvelteKit│────▶│  Go LLM    │────▶│  python-rag :8090     │  │
  │  │   app    │     │  server    │     │  (FastAPI)             │  │
  │  └──────────┘     └────────────┘     └────────────────────────┘  │
  │                                             │         │          │
  │                                        ┌───▼───┐ ┌───▼────┐      │
  │                                        │Chroma │ │Ollama  │      │
  │                                        │ :8000 │ │ :11434 │      │
  │                                        └───────┘ └────────┘      │
  │                                                                  │
  │  ┌──────────────────┐                                            │
  │  │  PostgreSQL :5432│◀── QAPair table (source of truth)         │
  │  └──────────────────┘                                            │

  
  Data flow — Index time (startup / admin sync):
  PostgreSQL QAPair rows
          ↓
    read all Q&A pairs
          ↓ (per pair)
    format: "Q: {question}\nA: {answer}"   ← single chunk per pair
          ↓
    embed via Ollama (nomic-embed-text)
          ↓
    upsert into ChromaDB (with metadata: topic, difficulty, id)
          ↓
    also load all texts into rank_bm25 BM25Index (RAM)

  Data flow — Query time:
  User question
          ↓
    embed question → dense search ChromaDB → top-20 results (with
  scores)
          ↓
    BM25 search in RAM → top-20 results (with scores)
          ↓
    RRF merge (Reciprocal Rank Fusion):
          score = Σ 1/(rank + 60)   ← 60 is the standard RRF constant
          ↓
    top-5 after merge → build prompt
          ↓
    Ollama chat (gemma4:e4b) → answer
          ↓
    return {answer, contexts}
    ===============================