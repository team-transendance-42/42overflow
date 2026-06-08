"""
Text embedding using fastembed (model controlled by EMBED_MODEL env var).

LRU cache on single-text embedding:
  At query time, embed_texts is called with one question. The same questions
  repeat across users (42 students ask similar things). An LRU cache avoids
  re-running the CPU-bound fastembed model for repeated questions.

Theory — lru_cache:
  functools.lru_cache wraps a function with an O(1) dict + doubly-linked list.
  On hit: one dict lookup, return cached value — no model call.
  On miss: call the function, store result, evict LRU entry if at maxsize.
  Thread-safe: protected by the GIL and an internal lock.
  Cache key: the function argument(s) — must be hashable (str is hashable).

Cache key normalisation:
  text.lower().strip() before lookup — "What is malloc?" and "what is malloc?"
  share one slot. The normalised text is what gets embedded (consistent).

Why single-text only, not batch:
  Startup embeds 200 unique docs in one batch call — all would miss the cache,
  adding N lookup overhead for zero benefit. The batch path bypasses the cache
  and calls _embed_sync directly (one model call for all N texts).

Pros:
  - Repeated questions: ~0ms (cache hit) vs ~100-300ms (CPU embed)
  - No new dependency — functools is stdlib
  - 512 slots × 768 floats × 4 bytes ≈ 1.5MB RAM (negligible)

Cons:
  - Cache is process-local; cleared on restart, not shared between workers
  - Novel (first-time) questions still pay full embed cost
  - Multi-text batch calls bypass the cache entirely

Edge cases:
  - asyncio.to_thread overhead on cache hit: ~0.01ms (acceptable)
  - cache_clear() must be called in tests to prevent cross-test contamination
  - NaN/inf in model output: not filtered here — callers handle it (detector.py)
"""

import asyncio
import hashlib
from functools import lru_cache

from fastembed import TextEmbedding

from config import EMBED_MODEL

# Loaded once at module import — stays in RAM, reused on every request.
# fastembed downloads the model to ~/.cache/fastembed/ on first use;
# the Dockerfile pre-downloads it at build time so container startup is instant.
# Model is controlled by EMBED_MODEL env var (see config.py):
#   BAAI/bge-small-en-v1.5        — 384-dim, ~100 MB RAM (default, memory-constrained)
#   nomic-ai/nomic-embed-text-v1.5 — 768-dim, ~2 GB RAM  (school computers)
_model = TextEmbedding(EMBED_MODEL)

# LRU cache size: 512 slots × dim × 4 bytes ≈ 0.75 MB (BAAI/384-dim) or 1.5 MB (nomic/768-dim).
# 512 is generous for a 42-school context — covers the most common questions.
_CACHE_SIZE = 512


def format_doc(question: str, answer: str, tags: list[str] | None = None) -> str:
    """Format a QA pair for BM25 indexing and embedding.

    Tags are appended so both BM25 and the embedding model see them.
    tags=None or [] produces the same output as before (backward compatible).
    """
    base = f"Q: {question}\nA: {answer}"
    if tags:
        base += f"\ntags: {' '.join(tags)}"
    return base


def make_doc_id(question: str) -> str:
    """Stable unique ID for a document, derived from the question text."""
    return hashlib.sha256(question.encode()).hexdigest()


def make_doc_hash(question: str, answer: str) -> str:
    return hashlib.sha256((question + answer).encode()).hexdigest()


def _embed_sync(texts: list[str]) -> list[list[float]]:
    """Synchronous batch embed. CPU-bound — must run in a thread pool."""
    return [vec.tolist() for vec in _model.embed(texts)]


@lru_cache(maxsize=_CACHE_SIZE)
def _embed_one_cached(text: str) -> tuple[float, ...]:
    """
    Embed a single normalised text with LRU caching.

    Returns tuple (not list) because lru_cache requires a hashable return
    value to be storable — callers convert back to list[float].

    Cache key = the 'text' argument, which callers must normalise
    (lower + strip) before calling this function.

    On cache miss: calls _embed_sync([text]) — CPU-bound, takes 100-300ms.
    On cache hit: returns the stored tuple — O(1), ~0ms.
    """
    return tuple(_embed_sync([text])[0])


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed texts using the local nomic-embed-text-v1.5 model.

    Single text (query time):
      Uses _embed_one_cached — repeated questions return in ~0ms.
      Key is normalised (lowercased + stripped) before cache lookup.

    Multiple texts (startup batch):
      Bypasses the cache and calls _embed_sync directly in the thread pool.
      Batch is faster than N individual calls; all unique at startup anyway.

    Runs in a thread pool — fastembed is CPU-bound and must not block
    the async event loop.

    Returns one 768-dim vector per input text.
    """
    if not texts:
        raise RuntimeError("embed_texts called with empty list")

    if len(texts) == 1:
        # Single text: check cache (normalise key first).
        key = texts[0].lower().strip()
        # asyncio.to_thread handles both cache miss (CPU-bound embed)
        # and cache hit (O(1) lookup — thread overhead ~0.01ms, acceptable).
        result_tuple = await asyncio.to_thread(_embed_one_cached, key)
        return [list(result_tuple)]

    # Batch path: startup embeds all docs at once — bypass cache.
    return await asyncio.to_thread(_embed_sync, texts)
