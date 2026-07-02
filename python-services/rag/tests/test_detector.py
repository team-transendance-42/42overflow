"""
Unit tests for detector.py topic centroid computation and detection.
Run: uv run python -m pytest tests/test_detector.py -v
No external services — pure math on fake vectors.
"""
import pytest
from detector import build_topic_centroids, detect_topic


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
