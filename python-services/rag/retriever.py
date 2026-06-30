"""
Hybrid retrieval: dense (numpy cosine) + sparse (BM25+) merged with RRF.
Topic-aware: centroid similarity narrows search to the detected topic first.

Flow:
  1. Embed question (fastembed, CPU-bound, runs in thread pool).
  2. Detect topic via centroid similarity (numpy, ~0.01ms).
  3. If confident topic detected: filter both numpy and BM25 to that topic.
  4. If filtered results < MIN_FILTERED: fall back to full corpus.
  5. RRF merge: combine ranked lists by position, not score magnitude.

Why numpy instead of ChromaDB for dense search:
  ChromaDB runs in a separate container — every query_dense call was a
  network roundtrip (~50–150ms). NumpyIndex does the same cosine similarity
  in ~0.05ms in-process with a single matrix-vector multiply. At 200 docs,
  brute-force beats HNSW even ignoring the network overhead.

Pros of this approach:
  - No network dependency at query time
  - Exact nearest neighbours (HNSW approximates)
  - Safe for concurrent async reads (matrix is immutable after build)

Edge cases handled:
  - Empty NumpyIndex → dense_hits=[], RRF still works from BM25 alone
  - topic_filter yields < MIN_FILTERED combined hits → fallback to full corpus
  - id_to_text miss (BM25-only hit with unknown id) → returns "" for text
"""
from collections import defaultdict

from bm25_index import BM25Index
from detector import detect_topic
from embedder import embed_texts
from numpy_index import NumpyIndex

_RRF_K = 60   # standard RRF constant — dampens rank-1 dominance
_MIN_FILTERED = 3    # if fewer results after topic filter, fall back to full corpus


    # 1. Embed question — needed for both dense retrieval and centroid detection.
    #    Runs in a thread pool (fastembed is CPU-bound, must not block event loop).
    #    On failure: log and fall back to BM25-only (has_embeddings=False).
async def hybrid_search(
    question:        str,
    bm25_index:      BM25Index,
    numpy_index:     NumpyIndex,
    id_to_text:      dict[str, str],
    id_to_topic:     dict[str, str],
    centroids:       dict[str, list[float]],
    top_k:           int = 5,
    topic_intro_ids: dict[str, str] | None = None,
) -> tuple[list[dict], float, bool]:
    """
    Retrieve top-k docs using topic-aware hybrid search.

    Args:
        question:        raw user question string.
        bm25_index:      built BM25Index (from app.state).
        numpy_index:     built NumpyIndex (from app.state) — replaces ChromaDB HTTP.
        id_to_text:      {doc_id: formatted_text} (from app.state).
        id_to_topic:     {doc_id: topic} (from app.state).
        centroids:       {topic: centroid_vector} (from app.state).
                         Empty dict → topic detection disabled, full corpus used.
        top_k:           number of results to return after merging.
        topic_intro_ids: {topic: intro_doc_id} — when provided and a topic is
                         detected, the intro doc is pinned at position 0 if it
                         is not already in the top-k results.  Defaults to None
                         (no pinning) for backwards compatibility.

    Returns:
        (results, best_similarity, has_embeddings) where:
        - results: [{"id": ..., "text": ..., "rrf_score": ..., "topic": ...}]
          sorted by descending rrf_score (best match first).
        - best_similarity: cosine similarity of the single best-matching doc
          across the full corpus (unfiltered). Used by the Go service as a
          semantic gate — questions with best_similarity < threshold are
          off-topic and Ollama is not called.
        - has_embeddings: True when NumpyIndex is built and best_similarity is
          meaningful. False when NumpyIndex is empty (embedding failed at
          startup) — Go skips the semantic gate and relies on RRF confidence alone.
    """
    question_embedding: list[float] | None = None
    try:
        question_embedding = (await embed_texts([question]))[0]
    except Exception as exc:
        print(f"[retriever] WARNING: embedding failed — falling back to BM25-only: {exc}")

    # 1b. Gate signal: best cosine against the FULL corpus (no topic filter).
    #     Only meaningful when embeddings are available.
    full_hits: list[dict] = []
    has_embeddings = False
    best_similarity = 0.0
    if question_embedding is not None:
        try:
            full_hits = numpy_index.search(question_embedding, n=20)
            has_embeddings = len(full_hits) > 0
            best_similarity = round(1.0 - full_hits[0]["distance"], 4) if has_embeddings else 0.0
        except Exception as exc:
            print(f"[retriever] WARNING: dense search failed — using BM25 only: {exc}")

    # 2. Detect topic from embedding vs centroids (no-op if centroids={} or no embedding).
    detected_topic = None
    if question_embedding is not None:
        try:
            detected_topic, _ = detect_topic(question_embedding, centroids)
        except Exception as exc:
            print(f"[retriever] WARNING: topic detection failed: {exc}")
    use_filter = detected_topic is not None

    # 3a. Filtered retrieval when topic is confidently detected.
    if use_filter and question_embedding is not None:
        try:
            dense_hits = numpy_index.search(question_embedding, n=20, topic_filter=detected_topic)
        except Exception as exc:
            print(f"[retriever] WARNING: filtered dense search failed: {exc}")
            dense_hits = full_hits
        try:
            sparse_hits = bm25_index.search(question, n=20, topic_filter=detected_topic)
        except Exception as exc:
            print(f"[retriever] WARNING: filtered BM25 search failed: {exc}")
            sparse_hits = []

        # 3b. Fallback: too few filtered results → reuse the full-corpus hits.
        if len(dense_hits) + len(sparse_hits) < _MIN_FILTERED:
            dense_hits = full_hits
            try:
                sparse_hits = bm25_index.search(question, n=20)
            except Exception as exc:
                print(f"[retriever] WARNING: BM25 fallback search failed: {exc}")
                sparse_hits = []
    else:
        # 4. Full corpus (no confident topic detected, centroids disabled, or no embedding).
        dense_hits = full_hits
        try:
            sparse_hits = bm25_index.search(question, n=20)
        except Exception as exc:
            print(f"[retriever] WARNING: BM25 search failed: {exc}")
            sparse_hits = []

    # 5. RRF merge: score each doc by rank position in each list.
    #    Formula: score += 1 / (rank + k)   where k=60 is the RRF constant.
    #    rank 0 (best) → 1/60 ≈ 0.0167.
    #    A doc ranked top-5 in BOTH lists beats a doc ranked #1 in only one.
    #    This is robust to score scale differences between dense and sparse.
    rrf_scores: dict[str, float] = defaultdict(float)
    for rank, hit in enumerate(dense_hits):
        rrf_scores[hit["id"]] += 1.0 / (rank + _RRF_K)
    for rank, hit in enumerate(sparse_hits):
        rrf_scores[hit["id"]] += 1.0 / (rank + _RRF_K)

    # 6. Sort by RRF score, take top_k, resolve text from id_to_text.
    #    NumpyIndex.search() returns "document" field, but id_to_text is the
    #    authoritative source — covers BM25-only hits not in dense results.
    dense_text: dict[str, str] = {hit["id"]: hit["document"] for hit in dense_hits}
    top_ids = sorted(rrf_scores, key=rrf_scores.__getitem__, reverse=True)[:top_k]

    results = []
    for id_ in top_ids:
        text = dense_text.get(id_) or id_to_text.get(id_, "")
        if not text:
            print(f"[retriever] WARNING: no text for {id_!r} — BM25-only hit missing from id_to_text")
        results.append({
            "id":        id_,
            "text":      text,
            "rrf_score": round(rrf_scores[id_], 6),
            "topic":     id_to_topic.get(id_, "unknown"),
        })

    # Pin intro doc: when a topic is detected and its intro doc is not already
    # in the top-k results, insert it at position 0.
    # Ensures vague queries always start with "what is X" context before detail entries.
    # At capacity (len == top_k): drop the last entry to keep the count stable.
    # Under capacity (len < top_k):  just prepend — spare slots exist, keep all docs.
    if detected_topic and topic_intro_ids:
        intro_id = topic_intro_ids.get(detected_topic)
        result_ids = {r["id"] for r in results}
        if intro_id and intro_id not in result_ids:
            intro_text = dense_text.get(intro_id) or id_to_text.get(intro_id, "")
            intro_doc = {
                "id":        intro_id,
                "text":      intro_text,
                "rrf_score": 0.0,
                "topic":     detected_topic,
            }
            tail = results[:-1] if len(results) >= top_k else results
            results = [intro_doc] + tail

    return results, best_similarity, has_embeddings
