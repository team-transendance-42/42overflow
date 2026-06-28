  bm25_index: BM25Index

a class instance wrapping the rank_bm25 library (BM25Plus). BM25 is a keyword ranking algorithm:

  - scores documents by how rare and how frequent a word is across the corpus
  - "git" appearing in 2/100 docs scores higher than "the" appearing in 100/100
  - returns {"id": ..., "score": float} — that score is the BM25 float, not the index itself
================================
numpy_index: NumpyIndex

a class instance. stores all doc embeddings as a (N, D) float32 matrix — N docs, D dimensions (768 for fastembed).
  At search time: one matrix-vector multiply (M @ q_hat) gives cosine similarity to all N docs simultaneously in ~0.05ms. It stores distance = 1 -
  cosine_similarity, so 0 = identical, 2 = opposite.
==================================
id_to_text: dict[str, str]

  {"sha256_of_question": "Q: What is git rebase?\nA: It rewrites...\nTags: git"}

  Maps doc_id → formatted Q&A text. Built as dict(zip(all_ids, all_texts)) in _prepare_corpus. Needed because BM25 hits only return an id — you
  need this dict to look up the actual text to send to the LLM.
=================================
id_to_topic: dict[str, str]

  {"sha256_of_question": "git"}

  Maps doc_id → topic name. Used to attach "topic" to each result dict so the Go service knows which subject area the retrieved context came from.
  Topic comes from the topic field in seed/DB pairs — it maps to the subject in your DB.
=================================
  centroids: dict[str, list[float]]

  {"git": [0.12, -0.34, ...], "docker": [0.09, 0.21, ...]}

  For each topic, the mean of all its document embedding vectors. Built in build_topic_centroids() in detector.py. At query time, the question
  embedding is compared against each centroid — whichever centroid is closest is the detected topic. Then search is filtered to just that topic's
  docs before the full corpus is searched.
=============================
 topic_intro_ids: dict[str, str]

  {"git": "sha256_of_what_is_git_question", "docker": "sha256_of_what_is_docker_question"}

  Maps topic → doc_id of its "intro" document — docs tagged with "intro" in their tags field in seed/DB. When a topic is detected, its intro doc
  is pinned to position 0 in the results, regardless of RRF score. This ensures vague questions like "tell me about git" always start with "what
  is git?" context before diving into specific answers.

