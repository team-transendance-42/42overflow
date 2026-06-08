"""
Unit tests for detector.py topic centroid computation and detection.
Run: uv run python -m pytest tests/test_detector.py -v
No external services — pure math on fake vectors.
"""
import pytest
from detector import build_topic_centroids, detect_topic, cosine_similarity


# ── cosine_similarity ────────────────────────────────────────────────────────

def test_cosine_identical_vectors():
    v = [1.0, 0.0, 0.5]
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-6


def test_cosine_orthogonal_vectors():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert abs(cosine_similarity(a, b)) < 1e-6


def test_cosine_opposite_vectors():
    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    assert abs(cosine_similarity(a, b) - (-1.0)) < 1e-6


def test_cosine_zero_vector_returns_zero():
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


# ── build_topic_centroids ────────────────────────────────────────────────────

def test_centroid_single_doc():
    """Centroid of one doc is that doc's embedding."""
    pairs = [{"topic": "codexion"}]
    embeddings = [[1.0, 2.0, 3.0]]
    centroids = build_topic_centroids(pairs, embeddings)
    assert "codexion" in centroids
    assert centroids["codexion"] == [1.0, 2.0, 3.0]


def test_centroid_average_of_two():
    """Centroid of two docs is their element-wise average."""
    pairs = [{"topic": "fly-in"}, {"topic": "fly-in"}]
    embeddings = [[1.0, 3.0], [3.0, 1.0]]
    centroids = build_topic_centroids(pairs, embeddings)
    assert centroids["fly-in"] == [2.0, 2.0]


def test_centroid_multiple_topics():
    pairs = [{"topic": "a"}, {"topic": "b"}, {"topic": "a"}]
    embeddings = [[1.0, 0.0], [0.0, 1.0], [3.0, 0.0]]
    centroids = build_topic_centroids(pairs, embeddings)
    assert "a" in centroids
    assert "b" in centroids
    # centroid of a: avg([1,0],[3,0]) = [2,0]
    assert centroids["a"] == [2.0, 0.0]
    assert centroids["b"] == [0.0, 1.0]


def test_centroid_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        build_topic_centroids([], [])


# ── detect_topic ─────────────────────────────────────────────────────────────

def test_detect_topic_clear_winner():
    """When question embedding points exactly at one centroid, detect it."""
    centroids = {
        "codexion": [1.0, 0.0],
        "fly-in": [0.0, 1.0],
    }
    topic, confidence = detect_topic([1.0, 0.0], centroids)
    assert topic == "codexion"
    assert confidence > 0.9


def test_detect_topic_no_centroids_returns_none():
    topic, confidence = detect_topic([1.0, 0.0], {})
    assert topic is None
    assert confidence == 0.0


def test_detect_topic_low_confidence_returns_none():
    """When all similarities are below threshold, return None."""
    # Two centroids at 90° to each other; query is at 45° (equidistant)
    centroids = {
        "a": [1.0, 0.0],
        "b": [0.0, 1.0],
    }
    topic, confidence = detect_topic([1.0, 1.0], centroids)
    # Both have similarity ~0.707; gap is 0 → below margin threshold → no detection
    assert topic is None


def test_detect_topic_returns_best_with_margin():
    """Detect succeeds only when best is clearly ahead of second-best."""
    centroids = {
        "codexion": [0.99, 0.01],
        "fly-in": [0.01, 0.99],
    }
    topic, confidence = detect_topic([1.0, 0.0], centroids)
    assert topic == "codexion"
    assert confidence >= 0.7


# ── numpy correctness ────────────────────────────────────────────────────────
# These tests verify that the numpy implementation produces the same results
# as the hand-verified reference values. They catch floating-point regressions
# if the implementation changes internally.

def test_cosine_known_value():
    """[1,1] vs [1,0] = cos(45°) = 1/sqrt(2) ≈ 0.7071."""
    result = cosine_similarity([1.0, 1.0], [1.0, 0.0])
    assert abs(result - (2 ** -0.5)) < 1e-6


def test_cosine_high_dim_matches_reference():
    """768-dim all-ones vectors → cosine = 1.0 (parallel)."""
    dim = 768
    a = [1.0] * dim
    b = [1.0] * dim
    result = cosine_similarity(a, b)
    assert abs(result - 1.0) < 1e-5


def test_centroid_high_dim_shape():
    """Centroid of 768-dim embeddings has the right dimension."""
    import random
    random.seed(42)
    dim = 768
    pairs = [{"topic": "norminette"}] * 10
    vecs = [[random.gauss(0, 1) for _ in range(dim)] for _ in range(10)]
    centroids = build_topic_centroids(pairs, vecs)
    assert len(centroids["norminette"]) == dim


def test_detect_topic_single_topic_always_detected_if_confident():
    """With one topic, margin = best_score → detected when score >= threshold."""
    centroids = {"git": [1.0, 0.0]}
    topic, confidence = detect_topic([1.0, 0.0], centroids)
    assert topic == "git"
    assert confidence == pytest.approx(1.0, abs=1e-5)

# ── speed ────────────────────────────────────────────────────────────────────
# 1000 cosine_similarity calls on 768-dim vectors must complete in < 200ms.
# This is a regression guard — if it regresses to Python loops it will fail.


def test_cosine_speed_1000_calls():
    import time
    import random
    random.seed(0)
    dim = 768
    a = [random.gauss(0, 1) for _ in range(dim)]
    b = [random.gauss(0, 1) for _ in range(dim)]

    start = time.perf_counter()
    for _ in range(1000):
        cosine_similarity(a, b)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Pure Python: ~5000ms for 1000 calls. numpy: ~3ms.
    # 200ms threshold is 60x generous — any regression to Python loops will fail.
    assert elapsed_ms < 200, f"cosine_similarity too slow: {elapsed_ms:.1f}ms for 1000 calls"
