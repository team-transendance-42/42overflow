"""
Run: docker exec -it 42overflow-ollama-1 /bin/bash
uv run python -m tests.test_embedder
Requires: Ollama running (docker compose up -d)
"""
import asyncio
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from embedder import embed_texts, format_doc, make_doc_hash, make_doc_id


def test_embed_texts_ollama_unreachable():
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="Could not reach Ollama"):
            asyncio.run(embed_texts(["hello"]))


def test_embed_texts_http_error():
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=MagicMock(status_code=500)
        )
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="Ollama returned HTTP error"):
            asyncio.run(embed_texts(["hello"]))


def test_embed_texts_missing_embeddings_key():
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"unexpected_key": []}
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="Ollama response missing 'embeddings'"):
            asyncio.run(embed_texts(["hello"]))


def test_embed_texts_timeout():
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.side_effect = httpx.TimeoutException("Request timed out")
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="Ollama timed out"):
            asyncio.run(embed_texts(["hello"]))


def test_helpers():
    assert format_doc("What is X?", "X is Y.") == "Q: What is X?\nA: X is Y."

    assert make_doc_id("What is X?") == make_doc_id("What is X?"), "ID must be stable"
    assert make_doc_id("What is X?") != make_doc_id("What is Y?"), "different Q → different ID"

    assert make_doc_hash("Q", "A") == make_doc_hash("Q", "A"), "hash must be stable"
    assert make_doc_hash("Q", "A1") != make_doc_hash("Q", "A2"), "hash must change with answer"
    assert make_doc_hash("Q1", "A") != make_doc_hash("Q2", "A"), "hash must change with question"

    print("✓ helpers: format, ID stability/uniqueness, hash sensitivity")


def test_embed_texts():
    result = asyncio.run(embed_texts(["hello world", "free the pointer"])) #  asyncio is used to execute code written with async def and await, from regular (non-async) code.

    assert isinstance(result, list), "result must be a list"
    assert len(result) == 2, f"expected 2 vectors, got {len(result)}"
    assert len(result[0]) > 0, "vector must not be empty"
    assert len(result[0]) == len(result[1]), "all vectors must be same length"
    assert all(isinstance(v, float) for v in result[0]), "vector values must be floats"

    print(f"✓ embed_texts: 2 vectors of length {len(result[0])}")


if __name__ == "__main__":
    test_helpers()
    test_embed_texts()
    print("\nAll embedder tests passed.")
