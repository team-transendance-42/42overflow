 A centroid is the geometric average (mean) of a set of vectors. In embedding space, each document is a
  high-dimensional point (768 floats). A topic centroid is the average position of all documents that
  belong to that topic.

  pairs: [{question, answer, topic: "git"}, ...]
  embeddings: [[0.1, 0.3, ...], ...]  ← same order as pairs

  1. Groups all embedding vectors by their topic label
  2. For each topic, stacks all its vectors into a matrix (N_docs x 768) and takes np.mean(axis=0) → one
  768-dim centroid vector
  3. Returns {"git": [0.12, ...], "docker": [0.44, ...], ...} — one vector per topic


  Why it's useful

  At query time, detect_topic() (detector.py:108) compares the user's question embedding against all
  centroids in one matrix multiply. The closest centroid tells you which topic the question is probably
  about, so the retrieval can be filtered/boosted for that topic.

  Example intuition

  - All "git" docs cluster around some region of embedding space
  - Their average = the "center" of the git cluster
  - A new question about git rebase will land near that center → high cosine similarity → detected as
  "git"

  Edge cases (already handled in code)

  ┌────────────────────────────────┬─────────────────────────────────────────────┐
  │              Case              │                  Behavior                   │
  ├────────────────────────────────┼─────────────────────────────────────────────┤
  │ Missing topic key              │ defaults to "unknown"                       │
  ├────────────────────────────────┼─────────────────────────────────────────────┤
  │ Only 1 doc in a topic          │ centroid = that doc's embedding             │
  ├────────────────────────────────┼─────────────────────────────────────────────┤
  │ Empty pairs list               │ raises ValueError                           │
  ├────────────────────────────────┼─────────────────────────────────────────────┤
  │ Low confidence or small margin │ detect_topic returns None — no forced guess │
  └────────────────────────────────┴─────────────────────────────────────────────┘

  The two thresholds at detector.py:29–30 (_CONFIDENCE_THRESHOLD = 0.70, _MARGIN_THRESHOLD = 0.08)
  prevent false positives when a question sits ambiguously between topics.
  ==================================

  The core idea: embeddings as points in space

  An embedding model (like nomic-embed-text, 768 dimensions) maps text into a high-dimensional vector
  space where semantic similarity = geometric proximity. Two sentences about memory allocation land near
  each other; one about sorting algorithms lands elsewhere. The 768 numbers are coordinates of a point
  in ℝ⁷⁶⁸.

  the QA pairs each have a topic label ("pointers", "memory", etc.). we want one representative vector per topic — the centroid.
  ------------------------------------
   What a centroid is mathematically

  Given N vectors belonging to topic T:

  v₁ = [0.1, 0.4, ..., 0.9]   ← embedding of doc 1
  v₂ = [0.2, 0.3, ..., 0.8]   ← embedding of doc 2
  v₃ = [0.0, 0.5, ..., 0.7]   ← embedding of doc 3

  centroid = (v₁ + v₂ + v₃) / 3
           = element-wise mean
           = [0.1, 0.4, 0.8]   ← "center of mass" of the topic

  This is the arithmetic mean in vector space — the same centroid you'd compute for 2D points on a map,
  but in 768 dimensions. It minimizes the sum of squared distances to all members of the group (the
  classic least-squares center).

  Why this works semantically: if your 5 pointer-arithmetic docs all cluster together in the embedding
  space, their average lands in the middle of that cluster. A new question about pointers will be close
  to that center, far from the memory-management centroid.
  ----------------------------------
  Why centroids work for classification (and their limits)

  Pros:
  - Zero training, zero hyperparameters. You add a new topic by adding seed data; centroids update at
  restart.
  - O(1) per topic at query time — one dot product against each centroid.
  - Interpretable: the centroid is literally "the average meaning" of your topic documents.

  Cons:
  - Assumes each topic is convex and unimodal in embedding space. If your "algorithms" topic has docs
  about sorting AND graph traversal, the centroid lands between two sub-clusters and represents neither
  well.
  - Sensitive to cluster imbalance: a topic with 50 docs dominates its centroid more coherently than a
  topic with 2 docs. The single-doc case is extreme — centroid = that one document.
  - No notion of intra-topic variance. Two topics that happen to have overlapping vocabulary will have
  close centroids regardless of intent.
  ---------------------------------
   Where it fits in the pipeline

  startup:
    pairs, embeddings = loaded from DB/Chroma
    topic_centroids = build_topic_centroids(pairs, embeddings)
                      → {"pointers": [...768 floats...], "memory": [...], ...}

  query time:
    q_embedding = embed(user_question)
    topic, confidence = detect_topic(q_embedding, topic_centroids)
    → retrieve only docs matching that topic from Chroma

  The centroid is a cheap proxy for "what does this topic mean geometrically." At query time,
  detect_topic does one matrix multiply (all centroids at once) to find which topic center the question
  is closest to — then uses that to filter retrieval.