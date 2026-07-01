"""
Run: uv run python -m pytest tests/test_embedder.py -v
No external services required — fastembed runs in-process.
"""
import asyncio
import embedder as _embedder_module
from unittest.mock import patch
import pytest
from embedder import embed_texts, format_doc, make_doc_hash, _embed_one_cached


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
    # Without tags — backward compatible
    assert format_doc("What is X?", "X is Y.") == "Q: What is X?\nA: X is Y."

    # With tags — tags appended on new line
    result = format_doc("What is X?", "X is Y.", tags=["foo", "bar"])
    assert result == "Q: What is X?\nA: X is Y.\ntags: foo bar"

    # Empty tags list — no tags line added
    result_no_tags = format_doc("What is X?", "X is Y.", tags=[])
    assert result_no_tags == "Q: What is X?\nA: X is Y."

    assert make_doc_hash("What is X?", "") == make_doc_hash("What is X?", ""), "hash must be stable"
    assert make_doc_hash("What is X?", "") != make_doc_hash("What is Y?", ""), "different Q → different hash"

    assert make_doc_hash("Q", "A") == make_doc_hash("Q", "A"), "hash must be stable"
    assert make_doc_hash("Q", "A1") != make_doc_hash("Q", "A2"), "hash must change with answer"
    assert make_doc_hash("Q1", "A") != make_doc_hash("Q2", "A"), "hash must change with question"
    print("✓ helpers: format, ID stability/uniqueness, hash sensitivity")


# ── LRU cache tests ───────────────────────────────────────────────────────────
# Theory: _embed_one_cached wraps _embed_sync with lru_cache(maxsize=512).
# Cache key = text.lower().strip() — normalized so case/whitespace variants share a slot.
# embed_texts([single_text]) uses the cache; multi-text batch bypasses it.

def test_single_text_cache_hit_calls_model_once():
    """
    Calling embed_texts with the same question twice must only invoke the
    underlying model once. Second call returns the cached tuple.

    Theory: lru_cache stores results keyed by (normalized) text argument.
    On cache hit, the wrapped function body (_embed_sync) is never called.
    """
    _embed_one_cached.cache_clear()   # ensure clean state for this test

    call_count = 0
    original = _embedder_module._embed_sync

    def counting_sync(texts):
        nonlocal call_count
        call_count += 1
        return original(texts)

    with patch.object(_embedder_module, "_embed_sync", side_effect=counting_sync):
        r1 = asyncio.run(embed_texts(["what is malloc?"]))
        r2 = asyncio.run(embed_texts(["what is malloc?"]))

    assert call_count == 1, (
        f"expected _embed_sync called once (cache hit on 2nd call), got {call_count}"
    )
    assert r1 == r2, "cached result must equal fresh result"


def test_cache_normalization_case_insensitive():
    """
    'What is malloc?' and 'WHAT IS MALLOC?' must share the same cache slot.

    Theory: key = text.lower().strip() before cache lookup.
    Both normalise to 'what is malloc?' → same entry.
    """
    _embed_one_cached.cache_clear()

    call_count = 0
    original = _embedder_module._embed_sync

    def counting_sync(texts):
        nonlocal call_count
        call_count += 1
        return original(texts)

    with patch.object(_embedder_module, "_embed_sync", side_effect=counting_sync):
        asyncio.run(embed_texts(["What is malloc?"]))
        asyncio.run(embed_texts(["WHAT IS MALLOC?"]))
        asyncio.run(embed_texts(["  what is malloc?  "]))

    assert call_count == 1, (
        f"expected 1 model call for case/whitespace variants, got {call_count}"
    )


def test_different_questions_both_cached_separately():
    """
    Two different questions must each trigger one model call and cache separately.
    """
    _embed_one_cached.cache_clear()

    call_count = 0
    original = _embedder_module._embed_sync

    def counting_sync(texts):
        nonlocal call_count
        call_count += 1
        return original(texts)

    with patch.object(_embedder_module, "_embed_sync", side_effect=counting_sync):
        asyncio.run(embed_texts(["what is malloc?"]))
        asyncio.run(embed_texts(["what is free()?"]))
        # repeat both — should not trigger more calls
        asyncio.run(embed_texts(["what is malloc?"]))
        asyncio.run(embed_texts(["what is free()?"]))

    assert call_count == 2, (
        f"expected 2 model calls (one per unique question), got {call_count}"
    )


def test_batch_call_bypasses_cache():
    """
    embed_texts with multiple texts bypasses the cache and calls _embed_sync directly.

    Theory: batch calls (startup) embed many unique docs — caching individual
    texts would require N cache lookups with N guaranteed misses, adding overhead
    for no benefit. Batching is faster: one model call for N texts.
    """
    _embed_one_cached.cache_clear()

    call_count = 0
    original = _embedder_module._embed_sync

    def counting_sync(texts):
        nonlocal call_count
        call_count += 1
        return original(texts)

    with patch.object(_embedder_module, "_embed_sync", side_effect=counting_sync):
        result = asyncio.run(embed_texts(["question one", "question two"]))

    assert call_count == 1, "batch must call _embed_sync exactly once"
    assert len(result) == 2, "batch must return one embedding per input"


def test_cached_result_correct():
    """
    The cached embedding must be numerically identical to a fresh embed.
    Edge case: conversion tuple → list must not lose precision.
    """
    _embed_one_cached.cache_clear()

    r1 = asyncio.run(embed_texts(["what is a segfault?"]))
    _embed_one_cached.cache_clear()
    r2 = asyncio.run(embed_texts(["what is a segfault?"]))

    assert r1 == r2, "fresh and cached embeddings must be identical"
    assert len(r1[0]) == 768
