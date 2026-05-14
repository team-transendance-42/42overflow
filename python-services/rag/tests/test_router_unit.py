import sys, os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from router import router


def _make_client(bm25=None):
    app = FastAPI()
    app.include_router(router)
    app.state.bm25 = bm25
    app.state.id_to_text = {}
    return TestClient(app)


def test_retrieve_returns_contexts_and_confidence():
    mock_hits = [
        {"id": "abc", "text": "Q: What is malloc?\nA: It allocates heap memory.", "rrf_score": 0.035},
        {"id": "def", "text": "Q: When to free?\nA: After every malloc call.",    "rrf_score": 0.020},
    ]

    with patch("router.hybrid_search", new=AsyncMock(return_value=mock_hits)):
        resp = _make_client(bm25=object()).post("/rag/retrieve", json={"question": "memory management"})

    assert resp.status_code == 200
    data = resp.json()
    assert "contexts"   in data
    assert "confidence" in data
    assert len(data["contexts"]) == 2
    assert data["confidence"] == pytest.approx(0.035)
    assert data["contexts"][0]["rrf_score"] == pytest.approx(0.035)


def test_retrieve_503_when_index_not_ready():
    resp = _make_client(bm25=None).post("/rag/retrieve", json={"question": "hello"})
    assert resp.status_code == 503


def test_retrieve_empty_contexts_gives_zero_confidence():
    with patch("router.hybrid_search", new=AsyncMock(return_value=[])):
        resp = _make_client(bm25=object()).post("/rag/retrieve", json={"question": "very obscure topic"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["contexts"]   == []
    assert data["confidence"] == pytest.approx(0.0)


def test_retrieve_rejects_empty_question():
    resp = _make_client(bm25=object()).post("/rag/retrieve", json={"question": ""})
    assert resp.status_code == 422  # Pydantic min_length=1 validation


def test_retrieve_502_when_hybrid_search_raises():
    with patch("router.hybrid_search", new=AsyncMock(side_effect=RuntimeError("Ollama timed out"))):
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
