"""
In-memory brute-force cosine similarity index using numpy.

Why this instead of ChromaDB at query time:
  ChromaDB HNSW is designed for millions of docs and adds a network roundtrip
  (~50–150ms) even when the data is trivially small. For 200 docs, a single
  matrix-vector multiply in C/BLAS is exact, ~0.05ms, and needs no network.

Theory — pre-normalised dot product trick:
  cosine(a, b) = dot(a, b) / (||a|| * ||b||)
  If both vectors are L2-normalised to unit length, ||a|| = ||b|| = 1, so:
  cosine(a_hat, b_hat) = dot(a_hat, b_hat)
  Pre-normalise all doc vectors once at build time → search is pure dot product.
  Matrix form: scores = M @ q_hat  where M is (N, D) normalised matrix.
  This is ONE BLAS dgemv call for all N docs simultaneously.

Pros:
  - ~0.05ms per search for N=200, D=768 (vs 50–150ms ChromaDB HTTP)
  - Exact results (HNSW approximates)
  - No network dependency at query time
  - Safe for concurrent async reads (matrix is immutable after build)

Cons:
  - Embeddings are RAM-only; lost on restart (recomputed at startup ~5s for 200 docs)
  - No runtime incremental update — restart required to pick up new docs
  - Does not scale past ~50k docs (HNSW wins there via sublinear search)

Edge cases:
  - Empty index (build never called) → search returns []
  - topic_filter that matches no doc → returns []
  - n > number of docs → clamped to doc count (avoids argpartition crash)
  - Zero-norm query → guard returns [] (cannot rank meaningfully)
  - Zero-norm doc embedding → normalised to safe direction (norm replaced by eps)
"""

import numpy as np


class NumpyIndex:
    """
    Immutable in-memory cosine similarity index.

    Usage:
        idx = NumpyIndex()
        idx.build(ids, embeddings, topics, documents)
        results = idx.search(query_embedding, n=20, topic_filter="git")

    Thread safety:
        build() must complete before search() is called.
        After build, all attributes are read-only — safe for concurrent reads.
    """

    def __init__(self) -> None:
        # Set by build(); None signals index is not ready.
        self._matrix: np.ndarray | None = None  # shape (N, D), float32, L2-normalised
        self._ids: list[str] = []
        self._topics: list[str] = []
        self._documents: list[str] = []

    def build(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        topics: list[str],
        documents: list[str],
    ) -> None:
        """
        Normalise and store all embeddings as a float32 matrix.

        Args:
            ids:        stable doc IDs, same order as embeddings.
            embeddings: raw embedding vectors (e.g. 768-dim floats).
            topics:     topic label per doc, same order.
            documents:  formatted text per doc, same order (returned by search).

        Edge cases:
            - Empty list → matrix = None, search() returns [].
            - Zero-norm embedding: norm replaced by 1e-9 (safe divide; similarity
              will be near-zero, so the doc ranks last — correct behaviour).
        """
        if not ids:
            self._matrix = None
            return

        matrix = np.array(embeddings, dtype=np.float32)   # (N, D)

        # L2-normalise each row: norms shape (N, 1)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)

        # Guard zero-norm rows: replace 0 with tiny epsilon so divide is safe.
        # A zero embedding has no meaningful direction → similarity ≈ 0 → ranks last.
        norms = np.where(norms == 0.0, 1e-9, norms)

        self._matrix = matrix / norms   # unit vectors
        self._ids = list(ids)
        self._topics = list(topics)
        self._documents = list(documents)

    def search(
        self,
        query_embedding: list[float],
        n: int = 20,
        topic_filter: str | None = None,
    ) -> list[dict]:
        """
        Return up to n docs ranked by cosine similarity (best first).

        Theory:
            q_hat = query / ||query||
            scores = self._matrix @ q_hat   # (N,) cosine similarities
            distance = 1 - similarity       # range [0, 2]; 0 = identical

        Returns:
            [{"id": str, "document": str, "distance": float}]
            sorted ascending by distance (= descending similarity).
            Returns [] if index is empty or query norm is zero.

        Args:
            query_embedding: raw query vector, same dimension as build embeddings.
            n:               max results; clamped to index size.
            topic_filter:    if set, only return docs with this topic label.
        """
        if self._matrix is None:
            return []

        q = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0.0:
            # Zero query has no direction — cannot rank by cosine similarity.
            return []
        q_hat = q / q_norm

        # All cosine similarities in one matrix-vector multiply.
        scores = self._matrix @ q_hat   # shape (N,)

        # Apply topic filter: set scores to -inf for non-matching docs so they
        # rank last and get cut off by the top-n slice. Post-filter is correct
        # because numpy has no metadata concept — score everything, then restrict.
        if topic_filter is not None:
            mask = np.array(
                [t != topic_filter for t in self._topics], dtype=bool
            )
            scores[mask] = -np.inf

        # Check if any valid score remains after filtering.
        if np.all(scores == -np.inf):
            return []

        # Clamp n to actual number of valid docs.
        valid_count = int(np.sum(scores > -np.inf))
        safe_n = min(n, valid_count)

        # argpartition: O(N) partial sort to find top-safe_n indices.
        # Full sort only needed for the top-safe_n slice (much faster than
        # sorting all N docs when N is large — irrelevant at 200 but good habit).
        top_indices_unordered = np.argpartition(scores, -safe_n)[-safe_n:]
        top_indices = top_indices_unordered[np.argsort(scores[top_indices_unordered])[::-1]]

        return [
            {
                "id": self._ids[i],
                "document": self._documents[i],
                # distance = 1 - cosine_similarity; range [0, 2]
                # 0 = identical direction, 2 = opposite direction
                "distance": float(1.0 - scores[i]),
            }
            for i in top_indices
        ]
