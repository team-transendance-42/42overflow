
  Startup (once, when the container starts)

  seed.json + Postgres
         ↓
    load_pairs()          ← all QA pairs in memory
         ↓
   format_doc()            ← "Question: ...\nAnswer: ...\nTags: ..."
         ↓
   embed_texts()           ← 768-float vector per doc(qa pair)  [fastembed model]
         ↓
   ChromaDB upsert         ← persistent storage (survives restart)
         ↓
   get_embeddings()        ← pull embeddings back out of Chroma
         ↓
   build_topic_centroids() ← one average vector per topic
         ↓
   NumpyIndex.build()      ← all vectors in RAM as a matrix
   BM25Index.build()       ← tokenized term-frequency index

  Everything lives in app.state — shared across all requests, built once.
  -----------------
    User question (string)
         ↓
   embed_texts([question])     ← question becomes a 768-float vector
         ↓
   detect_topic()              ← centroid similarity → "which topic is this?"
         ↓
   NumpyIndex.search()         ← dense: cosine similarity vs all docs
   BM25Index.search()          ← sparse: keyword overlap (BM25+)
         ↓ (both filtered to detected topic if confident)
   RRF merge                   ← combine ranked lists by rank position
         ↓
   top-k docs → Go service     ← Go injects them into Ollama prompt
--------------------
 1. Embeddings — "what is a vector?"

  The fastembed model reads text and outputs 768 numbers. These aren't arbitrary — they encode meaning.
  Words and sentences that mean similar things produce vectors that are close together in this
  768-dimensional space.

  "how do I free memory in C"    → [0.12, -0.34, 0.88, ...]  (768 numbers)
  "malloc and free in C"          → [0.11, -0.33, 0.87, ...]  (very close)
  "how to center a div in CSS"   → [-0.45, 0.22, -0.12, ...] (very far)

  Closeness is measured by cosine similarity — the angle between the two vectors:

  cos(θ) = dot(a, b) / (||a|| × ||b||)
  range: -1 (opposite) to 1 (identical direction)

  You embed each QA pair once at startup and store it in ChromaDB + NumpyIndex. ChromaDB is the
  persistent store (survives restarts). NumpyIndex is the fast in-memory search engine.
------------------------
 2. NumpyIndex — dense search

  At build time, you take all N document vectors and stack them into a matrix M of shape (N, 768),
  pre-normalised to unit length. This is the trick:

  cosine(a, b) = dot(a/||a||, b/||b||)

  If all rows are already unit-length:
  scores = M @ q_hat   ← ONE matrix multiply = all N cosine similarities at once

  This runs in ~0.05ms in-process. The alternative — asking ChromaDB via HTTP — costs 50–150ms per query
  (network roundtrip). For 200 docs, brute-force beats the fancy HNSW index.

  Result: a ranked list of docs by cosine distance to the question.
-----------------------------------
  3. BM25 — sparse search

  BM25+ (Best Match 25, Plus variant) is a keyword frequency algorithm — the backbone of search engines
  for 30 years. It scores documents based on:

  - TF (term frequency): how often a query word appears in the doc
  - IDF (inverse document frequency): rare words score higher than common words ("segfault" > "the")
  - length normalisation: short docs aren't penalised for not repeating words

  BM25+ score(doc, query) = Σ IDF(t) x TF_normalized(t, doc) + delta
  // The Σ sums over every query term t.

  Why BM25 alongside dense? Dense embeddings understand meaning but can miss exact keywords. If someone
  types "ft_printf", cosine similarity might rank a general printf explanation high. BM25 will rank a
  doc that literally contains "ft_printf" first. They complement each other.
-------------------------------------
 4. RRF — merging the two lists

  Reciprocal Rank Fusion solves a hard problem: BM25 scores and cosine similarities are on completely
  different scales — you can't just add them.

  RRF converts both to rank positions first:

  score(doc) = 1/(rank_in_dense + 60) + 1/(rank_in_sparse + 60)

  The constant 60 dampens the advantage of being #1. A doc ranked #3 in both lists beats a doc ranked #1
  in only one list. It rewards consistent agreement between the two retrieval methods.
-------------------------------------
  5. Why centroids instead of just doing the cosine search directly?

  The cosine search already gives you the most similar docs. The centroid's job is a different thing
  entirely — it's a fast, coarse topic classifier that runs before retrieval.

  Without topic detection:
  User: "what is norminette?"
  NumpyIndex searches ALL docs (all topics mixed together)
  → might return git docs, memory docs, printf docs alongside norm docs

  With centroid topic detection:
  User: "what is norminette?"
  centroid similarity → "this is a 'norminette' topic" (confidence 0.82)
  NumpyIndex searches ONLY norminette docs
  → results are much more focused

  Why not just use the per-doc cosine search to filter? Because you'd need to look at all results first,
  see what topic they cluster in, then re-run. The centroid gives you the topic in a single dot product
  against 5–10 topic vectors (not 200 doc vectors). It's both faster and cleaner.

  The centroid represents "what the average question about this topic looks like." If your 20 norminette
  QA pairs all embed near each other in the 768-dim space, their centroid sits in the middle of that
  cluster. A new norminette question lands near that centroid → high cosine similarity → topic detected.
---------------------------------
 Why one embedded vector per text (not multiple)?

  The embedding model reads the entire text and outputs one 768-dim vector. This is a deliberate design
  — the model's transformer architecture compresses all the words and their relationships into a single
  point in space.

  The tradeoff: a very long document with two different topics might get a "blended" vector that isn't
  great for either. That's why your format_doc() combines question + answer + tags — it gives the model
  the full context so the embedding is rich. Short, focused QA pairs embed better than long mixed
  documents.
----------------------------------

format_doc(question, answer, tags)

  Which produces something like:

  Question: how do I free memory after malloc?

  Answer: always call free() with the same pointer...

  Tags: memory

  That entire string — question + answer + tags concatenated — is what gets embedded into one 768-float
  vector. So one QA pair → one doc → one vector.























  