"""
Unit tests for NumpyIndex — in-memory brute-force cosine similarity search.

Theory:
  NumpyIndex stores all doc embeddings as a pre-normalised float32 matrix.
  search() does ONE matrix-vector multiply to score all docs simultaneously,
  then returns the top-n by ascending cosine distance (= descending similarity).

Run: uv run pytest tests/test_numpy_index.py -v
No external services needed — pure numpy, no ChromaDB, no fastembed.
"""
import pytest
import numpy as np

from numpy_index import NumpyIndex


# ── helpers ──────────────────────────────────────────────────────────────────

def _unit(v: list[float]) -> list[float]:
    """Return L2-normalised version of v (for constructing exact test vectors)."""
    arr = np.array(v, dtype=np.float64)
    norm = np.linalg.norm(arr)
    return (arr / norm).tolist()


# ── build ─────────────────────────────────────────────────────────────────────

def test_build_and_search_basic():
    """
    Three clearly separated vectors.
    Query equal to doc-A should rank doc-A first.
    """
    idx = NumpyIndex()
    idx.build(
        ids=["a", "b", "c"],
        embeddings=[[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]],
        topics=["t1", "t2", "t1"],
        documents=["doc A", "doc B", "doc C"],
    )
    results = idx.search([1.0, 0.0], n=3)

    assert results[0]["id"] == "a", f"expected 'a' first, got {results[0]['id']}"
    assert results[-1]["id"] == "c", f"expected 'c' last, got {results[-1]['id']}"
    assert len(results) == 3


def test_returns_document_field():
    """search() must include 'document' so retriever can resolve text."""
    idx = NumpyIndex()
    idx.build(
        ids=["x"],
        embeddings=[[1.0, 0.0]],
        topics=["topic"],
        documents=["hello world"],
    )
    results = idx.search([1.0, 0.0], n=1)
    assert results[0]["document"] == "hello world"


def test_distance_field_range():
    """
    Cosine distance = 1 - cosine_similarity.
    Identical vectors → distance ≈ 0.
    Opposite vectors → distance ≈ 2.
    """
    idx = NumpyIndex()
    idx.build(
        ids=["same", "opp"],
        embeddings=[[1.0, 0.0], [-1.0, 0.0]],
        topics=["t", "t"],
        documents=["same", "opposite"],
    )
    results = idx.search([1.0, 0.0], n=2)
    # sorted ascending by distance
    assert results[0]["id"] == "same"
    assert results[0]["distance"] == pytest.approx(0.0, abs=1e-5)
    assert results[1]["distance"] == pytest.approx(2.0, abs=1e-5)


def test_topk_clamping():
    """
    Requesting more results than docs returns all docs, not a crash.
    Edge case: n > len(ids) must be clamped.
    """
    idx = NumpyIndex()
    idx.build(
        ids=["a", "b"],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        topics=["t", "t"],
        documents=["A", "B"],
    )
    results = idx.search([1.0, 0.0], n=100)
    assert len(results) == 2, f"expected 2 results (clamped), got {len(results)}"


def test_empty_index_returns_empty_list():
    """
    search() on an unbuilt index must return [] without raising.
    Edge case: empty matrix → no numpy call.
    """
    idx = NumpyIndex()
    results = idx.search([1.0, 0.0], n=5)
    assert results == []


def test_topic_filter_restricts_results():
    """
    topic_filter='t1' must return only docs with topic 't1'.
    Theory: post-filter after scoring (BM25 does same — no concept of metadata in numpy).
    """
    idx = NumpyIndex()
    idx.build(
        ids=["a", "b", "c"],
        embeddings=[[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]],
        topics=["t1", "t2", "t1"],
        documents=["A", "B", "C"],
    )
    results = idx.search([1.0, 0.0], n=3, topic_filter="t1")
    ids_returned = {r["id"] for r in results}
    assert ids_returned == {"a", "c"}, \
        f"topic_filter='t1' should return a and c, got {ids_returned}"
    assert all(r["id"] != "b" for r in results)


def test_topic_filter_no_match_returns_empty():
    """
    topic_filter that matches no doc → return [].
    Retriever's fallback handles this case.
    """
    idx = NumpyIndex()
    idx.build(
        ids=["a"],
        embeddings=[[1.0, 0.0]],
        topics=["t1"],
        documents=["A"],
    )
    results = idx.search([1.0, 0.0], n=5, topic_filter="nonexistent")
    assert results == []


def test_zero_query_returns_empty():
    """
    All-zero query vector → norm = 0 → guard must return [] without crash.
    Edge case: fastembed could theoretically return a zero embedding for empty input.
    """
    idx = NumpyIndex()
    idx.build(
        ids=["a"],
        embeddings=[[1.0, 0.0]],
        topics=["t1"],
        documents=["A"],
    )
    results = idx.search([0.0, 0.0], n=5)
    assert results == []


def test_results_sorted_ascending_distance():
    """
    Results must be sorted by ascending distance (best match first).
    """
    idx = NumpyIndex()
    # doc angles: 0°, 45°, 90° from query [1, 0]
    idx.build(
        ids=["90deg", "45deg", "0deg"],
        embeddings=[
            [0.0, 1.0],          # 90° → similarity=0, distance=1
            [1.0, 1.0],          # 45° → similarity≈0.707, distance≈0.293
            [1.0, 0.0],          # 0°  → similarity=1, distance=0
        ],
        topics=["t", "t", "t"],
        documents=["C", "B", "A"],
    )
    results = idx.search([1.0, 0.0], n=3)
    assert results[0]["id"] == "0deg", f"closest should be 0deg, got {results[0]['id']}"
    assert results[1]["id"] == "45deg", f"second should be 45deg, got {results[1]['id']}"
    assert results[2]["id"] == "90deg", f"farthest should be 90deg, got {results[2]['id']}"


def test_deterministic():
    """Same query always returns same ordering — no randomness in numpy argpartition."""
    idx = NumpyIndex()
    import random
    random.seed(99)
    dim = 768
    vecs = [[random.gauss(0, 1) for _ in range(dim)] for _ in range(20)]
    idx.build(
        ids=[str(i) for i in range(20)],
        embeddings=vecs,
        topics=["t"] * 20,
        documents=[f"doc {i}" for i in range(20)],
    )
    q = [random.gauss(0, 1) for _ in range(dim)]
    first = [r["id"] for r in idx.search(q, n=5)]
    second = [r["id"] for r in idx.search(q, n=5)]
    assert first == second, "search must be deterministic"


# ── speed ─────────────────────────────────────────────────────────────────────

def test_search_speed_200_docs():
    """
    200 docs × 768 dim: 1000 searches must complete in < 500ms.
    Regression guard: if we accidentally regress to Python loops this fails.
    Numpy target: ~0.05ms per search → 1000 calls ≈ 50ms.
    """
    import time
    import random
    random.seed(7)
    dim = 768
    n = 200
    vecs = [[random.gauss(0, 1) for _ in range(dim)] for _ in range(n)]
    q = [random.gauss(0, 1) for _ in range(dim)]

    idx = NumpyIndex()
    idx.build(
        ids=[str(i) for i in range(n)],
        embeddings=vecs,
        topics=["t"] * n,
        documents=[f"doc {i}" for i in range(n)],
    )

    start = time.perf_counter()
    for _ in range(1000):
        idx.search(q, n=5)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # 2000ms threshold: numpy target ~50ms, pure Python would be ~50,000ms.
    # Generous budget for full-suite CPU load (fastembed threads, WSL2 overhead).
    # Still catches any real regression to Python loops (25x safety margin).
    assert elapsed_ms < 2000, f"NumpyIndex too slow: {elapsed_ms:.1f}ms for 1000 searches"
