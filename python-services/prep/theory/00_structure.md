  python-services/rag/
  ├── main.py          # FastAPI app, startup sync, route wiring
  ├── config.py        # env vars (OLLAMA_URL,
  CHROMA_URL, etc.)
  ├── seed.py          # 40 hardcoded Q&A pairs + load_seed() function
  ├── db.py            # PostgreSQL client — read QAPairs via raw
  asyncpg queries
  │                    #   (no ORM, no Prisma client — Python service
  talks directly)
  ├── embedder.py      # embed_texts(texts) → calls Ollama /api/embed
  ├── store.py         # ChromaDB client — upsert_qa(), query_dense()
  ├── bm25_index.py    # BM25 wrapper — build(docs), search(query, n) →
  ranked list
  ├── retriever.py     # hybrid_search(question, top_k) — runs
  dense+BM25, applies RRF
  ├── generator.py     # ask_ollama(prompt) → answer string
  ├── router.py        # /rag/index, /rag/ask, /healthz, /admin/sync
  endpoints
  └── pyproject.toml   # add: asyncpg, chromadb-client, rank_bm25, httpx

  Each module's single responsibility:

  File: seed.py
  Does exactly one thing: Owns the 40 Q&A pairs. Nothing else.
  ────────────────────────────────────────
  File: db.py
  Does exactly one thing: Reads QAPair rows from Postgres. No business
    logic.
  ────────────────────────────────────────
  File: embedder.py
  Does exactly one thing: HTTP call to Ollama embed. Returns
    list[list[float]].
  ────────────────────────────────────────
  File: store.py
  Does exactly one thing: CRUD on ChromaDB. Knows nothing about BM25 or
    the LLM.
  ────────────────────────────────────────
  File: bm25_index.py
  Does exactly one thing: Pure BM25 math. No I/O. Accepts plain strings.
  ────────────────────────────────────────
  File: retriever.py
  Does exactly one thing: Orchestrates dense + sparse + RRF. Calls
    embedder, store, bm25.
  ────────────────────────────────────────
  File: generator.py
  Does exactly one thing: One function: sends prompt to Ollama chat,
    returns answer string.
  ────────────────────────────────────────
  File: router.py
  Does exactly one thing: FastAPI routes only. Calls retriever +
    generator. No business logic.
  ────────────────────────────────────────
  File: main.py
  Does exactly one thing: Wires everything at startup. Runs the sync.
    Mounts the router.

    Startup sequence in main.py:
  1. try connect to Postgres
  2a. if QAPair table exists → load all rows
  2b. else → load from seed.py (fallback)
  3. embed all docs → upsert into ChromaDB
  4. build BM25 index in RAM from same docs
  5. start FastAPI, mount router
===========================
 Hybrid Retrieval — BM25 + Dense + RRF
 -------------------------

 
  Query type: "what causes undefined behavior"
  Dense wins: ✓ semantic match
  BM25 wins: misses — no exact keywords
  ────────────────────────────────────────
  Query type: "ft_printf %d flag"
  Dense wins: weak — %d has no embedding meaning
  BM25 wins: ✓ exact token match
  ───────────────────────────────────
  Query type: "segfault when freeing struct"
  Dense wins: ✓
  BM25 wins: ✓ both fire

RRF — Reciprocal Rank Fusion (the merge math):
  # Each retriever returns a ranked list. RRF combines by rank position,
   not score.
  # score(doc) = Σ  1 / (rank_in_list + k)   where k=60 (standard
  constant)

  # Example: doc "double free is UB" retrieved as:
  #   dense rank 3  → 1/(3+60)  = 0.0159
  #   BM25  rank 1  → 1/(1+60)  = 0.0164
  #   RRF total     = 0.0323    ← beats a doc that ranked 1st in only
  one list

  
  The k=60 constant dampens the influence of very high ranks — a rank-1
  result doesn't dominate everything else. This is why RRF consistently
  outperforms score-based fusion.

  retriever.py logic (pseudocode you'll implement):
  async def hybrid_search(question: str, top_k: int = 5):
      # 1. dense search — ask ChromaDB for top-20
      dense_results = await store.query_dense(question_embedding, n=20)
      # returns: [{"id": "qa-3", "document": "Q: ...A: ...", "distance":
   0.12}, ...]

      # 2. sparse search — BM25 in RAM, top-20
      bm25_results = bm25_index.search(question, n=20)
      # returns: [{"id": "qa-3", "score": 4.2}, ...]

      # 3. RRF merge
      scores = defaultdict(float)
      for rank, hit in enumerate(dense_results):
          scores[hit["id"]] += 1 / (rank + 60)
      for rank, hit in enumerate(bm25_results):
          scores[hit["id"]] += 1 / (rank + 60)

      # 4. sort by RRF score, return top_k documents
      top_ids = sorted(scores, key=scores.get, reverse=True)[:top_k]
      return [id_to_document[id] for id in top_ids]

  bm25_index.py — what rank_bm25 gives you:
  from rank_bm25 import BM25Okapi

  # BM25 Okapi variant — the same formula used by Elasticsearch
  # BM25(q,d) = Σ IDF(qi) * (tf * (k1+1)) / (tf + k1*(1-b+b*|d|/avgdl))
  # k1=1.5 (term saturation), b=0.75 (length normalization) — standard
  defaults

  class BM25Index:
      def build(self, documents: list[str], ids: list[str]):
          tokenized = [doc.lower().split() for doc in documents]
          self.bm25 = BM25Okapi(tokenized)
          self.ids = ids

      def search(self, query: str, n: int = 20) -> list[dict]:
          scores = self.bm25.get_scores(query.lower().split())
          top_n = sorted(enumerate(scores), key=lambda x: x[1],
  reverse=True)[:n]
          return [{"id": self.ids[i], "score": s} for i, s in top_n if s
   > 0]

  The prompt sent to Ollama after retrieval:
  You are a helpful assistant for 42 school students.
  Use ONLY the context below to answer. If unsure, say so briefly.

  Context:
  [1] Q: What happens if you free() a pointer twice?
      A: Double free is undefined behavior...

  [2] Q: What is the difference between stack and heap?
      A: Stack is automatically managed...

  Question: explain why my program crashes after free()

