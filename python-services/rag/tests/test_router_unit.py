import sys
import os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from router import router  # noqa: E402
from metrics import Metrics  # noqa: E402


def _make_client(bm25=None):
    from numpy_index import NumpyIndex
    app = FastAPI()
    app.include_router(router)
    app.state.bm25 = bm25
    app.state.numpy_index = NumpyIndex()
    app.state.id_to_text = {}
    app.state.id_to_topic = {}
    app.state.centroids = {}
    app.state.topic_intro_ids = {}
    app.state.metrics = Metrics()
    return TestClient(app)


def test_retrieve_returns_contexts_and_confidence():
    mock_hits = [
        {"id": "abc", "text": "Q: What is malloc?\nA: It allocates heap memory.",
         "rrf_score": 0.035},
        {"id": "def", "text": "Q: When to free?\nA: After every malloc call.",
         "rrf_score": 0.020},
    ]

    with patch("router.hybrid_search", new=AsyncMock(return_value=(mock_hits, 0.85, True))):
        resp = _make_client(
            bm25=object()).post(
            "/rag/retrieve",
            json={
                "question": "memory management"})

    assert resp.status_code == 200
    data = resp.json()
    assert "contexts" in data
    assert "confidence" in data
    assert len(data["contexts"]) == 2
    assert data["confidence"] == pytest.approx(0.035)
    assert data["contexts"][0]["rrf_score"] == pytest.approx(0.035)


def test_retrieve_503_when_index_not_ready():
    resp = _make_client(bm25=None).post("/rag/retrieve", json={"question": "hello"})
    assert resp.status_code == 503


def test_retrieve_empty_contexts_gives_zero_confidence():
    with patch("router.hybrid_search", new=AsyncMock(return_value=([], 0.0, True))):
        resp = _make_client(
            bm25=object()).post(
            "/rag/retrieve",
            json={
                "question": "very obscure topic"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["contexts"] == []
    assert data["confidence"] == pytest.approx(0.0)


def test_retrieve_rejects_empty_question():
    resp = _make_client(bm25=object()).post("/rag/retrieve", json={"question": ""})
    assert resp.status_code == 422  # Pydantic min_length=1 validation


def test_retrieve_502_when_hybrid_search_raises():
    with patch("router.hybrid_search",
               new=AsyncMock(side_effect=RuntimeError("Ollama timed out"))):
        resp = _make_client(bm25=object()).post("/rag/retrieve", json={"question": "malloc"})

    assert resp.status_code == 502
    assert "Ollama timed out" in resp.json()["detail"]


def test_ask_502_when_hybrid_search_raises():
    with patch("router.hybrid_search", new=AsyncMock(side_effect=RuntimeError("embed failed"))):
        resp = _make_client(bm25=object()).post("/rag/ask", json={"question": "segfault"})

    assert resp.status_code == 502


def test_ask_502_when_generate_raises():
    mock_hits = [{"id": "x", "text": "Q: foo\nA: bar", "rrf_score": 0.03}]
    with patch("router.hybrid_search", new=AsyncMock(return_value=mock_hits)), \
            patch("router.generate", new=AsyncMock(side_effect=Exception("Ollama down"))):
        resp = _make_client(bm25=object()).post("/rag/ask", json={"question": "segfault"})

    assert resp.status_code == 502


def test_retrieve_passes_top_k_4_to_hybrid_search():
    with patch("router.hybrid_search", new=AsyncMock(return_value=([], 0.0, True))) as mock_search:
        _make_client(bm25=object()).post("/rag/retrieve", json={"question": "malloc"})

    call_kwargs = mock_search.call_args.kwargs
    assert call_kwargs.get("top_k") == 4, f"expected top_k=4, got {call_kwargs}"


def test_ask_passes_top_k_4_to_hybrid_search():
    mock_hits = [{"id": "x", "text": "Q: foo\nA: bar", "rrf_score": 0.03}]
    with patch("router.hybrid_search", new=AsyncMock(return_value=(mock_hits, 0.85, True))) as mock_search, \
            patch("router.generate", new=AsyncMock(return_value="an answer")):
        _make_client(bm25=object()).post("/rag/ask", json={"question": "malloc"})

    call_kwargs = mock_search.call_args.kwargs
    assert call_kwargs.get("top_k") == 4, f"expected top_k=4, got {call_kwargs}"


def test_retrieve_passes_topic_intro_ids_to_hybrid_search():
    """Router must forward topic_intro_ids from app.state to hybrid_search."""
    with patch("router.hybrid_search", new=AsyncMock(return_value=([], 0.0, True))) as mock_search:
        _make_client(bm25=object()).post("/rag/retrieve", json={"question": "malloc"})

    call_kwargs = mock_search.call_args.kwargs
    assert "topic_intro_ids" in call_kwargs, (
        f"expected topic_intro_ids kwarg, got: {list(call_kwargs.keys())}"
    )


def test_retrieve_increments_retrieve_total():
    """Every /rag/retrieve call must increment retrieve_total by 1."""
    with patch("router.hybrid_search", new=AsyncMock(return_value=([], 0.0, True))):
        client = _make_client(bm25=object())
        client.post("/rag/retrieve", json={"question": "malloc"})
        assert client.app.state.metrics.retrieve_total == 1


def test_retrieve_increments_retrieve_errors_on_502():
    """hybrid_search exception must increment retrieve_errors."""
    with patch("router.hybrid_search",
               new=AsyncMock(side_effect=RuntimeError("embed failed"))):
        client = _make_client(bm25=object())
        resp = client.post("/rag/retrieve", json={"question": "malloc"})
        assert resp.status_code == 502
        assert client.app.state.metrics.retrieve_errors == 1
        assert client.app.state.metrics.retrieve_total == 1


def test_retrieve_increments_retrieve_errors_on_503():
    """503 (index not ready) must increment both retrieve_total and retrieve_errors."""
    client = _make_client(bm25=None)
    resp = client.post("/rag/retrieve", json={"question": "malloc"})
    assert resp.status_code == 503
    assert client.app.state.metrics.retrieve_total == 1
    assert client.app.state.metrics.retrieve_errors == 1


def test_retrieve_increments_bm25_only_fallbacks_when_no_embeddings():
    """has_embeddings=False must increment bm25_only_fallbacks."""
    with patch("router.hybrid_search", new=AsyncMock(return_value=([], 0.0, False))):
        client = _make_client(bm25=object())
        client.post("/rag/retrieve", json={"question": "malloc"})
        assert client.app.state.metrics.bm25_only_fallbacks == 1


def test_retrieve_does_not_increment_bm25_only_when_embeddings_present():
    """has_embeddings=True must NOT increment bm25_only_fallbacks."""
    with patch("router.hybrid_search", new=AsyncMock(return_value=([], 0.0, True))):
        client = _make_client(bm25=object())
        client.post("/rag/retrieve", json={"question": "malloc"})
        assert client.app.state.metrics.bm25_only_fallbacks == 0
