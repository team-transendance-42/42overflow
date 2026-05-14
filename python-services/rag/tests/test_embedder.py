"""
Run: uv run python -m pytest tests/test_embedder.py -v
No external services required — fastembed runs in-process.
"""
import asyncio
from unittest.mock import patch
import pytest
from embedder import embed_texts, format_doc, make_doc_hash, make_doc_id


def test_embed_texts_no_http():
    """embed_texts must not make any HTTP calls — fastembed runs in-process.

    Patches httpx.AsyncClient to raise immediately.
    Old code (Ollama HTTP): raises RuntimeError → test FAILS.
    New code (fastembed):   httpx never called  → test PASSES.
    """
    with patch("httpx.AsyncClient") as mock:
        mock.side_effect = RuntimeError("no network allowed")
        result = asyncio.run(embed_texts(["segfault"]))
    assert isinstance(result, list)
    assert len(result) == 1


def test_embed_texts_returns_768d_vectors():
    result = asyncio.run(embed_texts(["what is a segfault?", "how to use malloc in C"]))
    assert len(result) == 2
    assert len(result[0]) == 768          # nomic-embed-text-v1.5 output dimension
    assert len(result[0]) == len(result[1])
    assert all(isinstance(v, float) for v in result[0])


def test_embed_texts_empty_raises():
    with pytest.raises(RuntimeError, match="empty list"):
        asyncio.run(embed_texts([]))


def test_helpers():
    assert format_doc("What is X?", "X is Y.") == "Q: What is X?\nA: X is Y."

    assert make_doc_id("What is X?") == make_doc_id("What is X?"), "ID must be stable"
    assert make_doc_id("What is X?") != make_doc_id("What is Y?"), "different Q → different ID"

    assert make_doc_hash("Q", "A") == make_doc_hash("Q", "A"), "hash must be stable"
    assert make_doc_hash("Q", "A1") != make_doc_hash("Q", "A2"), "hash must change with answer"
    assert make_doc_hash("Q1", "A") != make_doc_hash("Q2", "A"), "hash must change with question"
    print("✓ helpers: format, ID stability/uniqueness, hash sensitivity")
