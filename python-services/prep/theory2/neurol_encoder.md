  Imagine you have a giant library and you're looking for books about "cars."

  Keyword search is like a librarian who only reads the index cards. If a book says "automobile" instead of "car," the librarian says "nope, doesn't
   match" — even though it's the same thing. She's just matching letters, not understanding meaning.

  A neural encoder is like a librarian who has read every book ever written and understands what things mean. She knows "car," "automobile,"
  "vehicle," and "ride" are all related. She groups books by meaning, not by spelling.

  How did she get so smart? She studied billions of sentences where "car" and "automobile" appeared in the same context (like "I drive my
  car/automobile to work"). Over time, she learned they mean the same thing — without anyone telling her directly.

  When you ask her a question, she doesn't search for matching words. She asks: "what does this question mean?" and finds content that means
  something similar.

  ---
  For a developer

  The problem with keyword search (BM25/TF-IDF): BM(best matching)25 and TF-IDF (term frequency-inverse document frequency) are based on counting words. They create a huge sparse vector(sparse: most values are zero, vector in .py: arr of nums) where each dimension(position in vector, index) corresponds to a word in the vocabulary.

  Words are represented as independent dimensions in a sparse vector space. "car" and "automobile" have zero overlap — their dot product is 0. The
  vocabulary matrix has ~50K+ dimensions, almost all zeros.

  "car"        → [0, 0, 1, 0, 0, ..., 0]  # dimension 1842
  "automobile" → [0, 0, 0, 0, 1, ..., 0]  # dimension 7103
  cosine_sim   → 0.0  ← totally orthogonal

  Retrieval fails silently. No error, just wrong results.

  Dense embeddings fix this:

  A neural encoder (transformer-based) maps text into a continuous vector space of ~768–1536 dimensions where semantic similarity ≈ geometric
  proximity.

  embed("car")        → [0.21, -0.43, 0.87, ...]  # 768-dim
  embed("automobile") → [0.22, -0.41, 0.85, ...]  # very close!
  cosine_sim          → ~0.97  ← nearly identical

  How the encoder learns this:

  Training on contrastive objectives (e.g., SimCSE, MNRL) over billions of sentence pairs:

  # Positive pairs (should be close):
  ("I drove my car", "I drove my automobile")
  ("What's the weather?", "Is it raining?")

  # Negative pairs (should be far):
  ("I drove my car", "The recipe uses flour")

  The model learns to minimize distance between semantically equivalent sentences and maximize distance between unrelated ones. After seeing enough
  examples, synonyms, paraphrases, and conceptually related ideas all cluster together.

  Models in production:

  ┌────────────────────────┬──────┬─────────────────────────────────┐
  │         Model          │ Dims │              Notes              │
  ├────────────────────────┼──────┼─────────────────────────────────┤
  │ nomic-embed-text       │ 768  │ Open, runs locally, strong perf │
  ├────────────────────────┼──────┼─────────────────────────────────┤
  │ text-embedding-3-small │ 1536 │ OpenAI API, cheap               │
  ├────────────────────────┼──────┼─────────────────────────────────┤
  │ text-embedding-3-large │ 3072 │ OpenAI API, best quality        │
  └────────────────────────┴──────┴─────────────────────────────────┘

  In your RAG pipeline, you replace the TF-IDF index with an ANN (approximate nearest neighbor) index like FAISS or pgvector, store the dense
  vectors, and query with cosine_similarity instead of BM25 score.

  # Instead of:
  results = bm25.get_top_n(query.split(), docs, n=5)

  # You do:
  q_vec = embed(query)           # [768-dim float]
  results = index.search(q_vec, k=5)  # cosine ANN search

  The key insight: meaning lives in geometry, not in character sequences.