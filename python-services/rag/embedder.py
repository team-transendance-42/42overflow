"""
Text embedding using fastembed (model controlled by EMBED_MODEL env var).
fastembed.TextEmbedding converts any text chunk into a fixed-size float vector:
  1. Tokenizes the text
  2. Runs it through a transformer (ONNX under the hood)
  3. Mean-pools the token embeddings → one fixed-size vector
  4. Optionally L2-normalizes it

Output dimension depends on the model (nomic-ai/nomic-embed-text-v1.5 → 768 floats).
Chunk size does not change the dimension — a 10-word chunk and a 500-word chunk
both produce the same 768 floats. Very long chunks are truncated at the model's
token limit (~512 tokens), so extremely large chunks lose their tail content.

The dot product / cosine similarity happens at search time inside pgvector,
fastembed only produces the vectors.

!!NB!! fastembed is CPU-bound — There is no "waiting", just pure computation. If you run
  it directly in the async function it blocks the entire event loop — no other request can be answered
  for 100-300ms. That's a freeze.
  A thread pool is a pre-created set of OS threads that sit idle, waiting for work. When you submit a
  job to it, an idle thread picks it up and runs it. The thread pool in Python's asyncio is called
  ThreadPoolExecutor and it's created automatically.
"""

import asyncio
import hashlib
from functools import lru_cache

from fastembed import TextEmbedding

from config import EMBED_MODEL

# Loaded once at module import — stays in RAM, reused on every request.
# fastembed downloads the model to ~/.cache/fastembed/ on first use;
# the Dockerfile pre-downloads it at build time so container startup is instant.
try:
    _model: TextEmbedding | None = TextEmbedding(EMBED_MODEL)
except Exception as _load_exc:
    print(f"[embedder] FATAL: failed to load embedding model '{EMBED_MODEL}': {_load_exc}")
    _model = None

# LRU cache size: 512 slots x dim x 4 bytes ≈ 1.5 MB (nomic/768-dim).
_CACHE_SIZE = 512


def format_doc(question: str, answer: str, tags: list[str] | None = None) -> str:
    """Format a QA pair for BM25 indexing and embedding.

    Tags are appended so both BM25 and the embedding model see them.
    """
    base = f"Q: {question}\nA: {answer}"
    if tags:
        base += f"\ntags: {' '.join(tags)}"
    return base


def make_doc_hash(question: str, answer: str) -> str:
    """SHA-256 fingerprint of a question+answer pair. Used as the change-detection hash."""
    return hashlib.sha256((question + answer).encode()).hexdigest()


def make_doc_id(pair: dict) -> str:
    """Stable Chroma document ID for a Q&A pair.
    DB pairs carry an 'id' field (e.g. 'db-comment-42') that is stable across edits.
    Seed pairs are immutable files, so hash(question) is stable enough."""
    if "id" in pair:
        return pair["id"]
    return hashlib.sha256(pair["question"].encode()).hexdigest()


def _embed_sync(texts: list[str]) -> list[list[float]]:
    """Synchronous batch embed. CPU-bound — must run in a thread pool."""
    if _model is None:
        raise RuntimeError(f"Embedding model '{EMBED_MODEL}' failed to load at startup")
    try:
        return [vec.tolist() for vec in _model.embed(texts)]
    except Exception as exc:
        raise RuntimeError(f"Embedding failed for {len(texts)} text(s): {exc}") from exc


# lru cache takes the return value of _embed_one_cached and stores it in RAM for future calls with the same key.
# we dont need to call the func: the decorator does that for us. the cache is cleared on container restart, so the first call after restart will take 100-300ms, but subsequent calls with the same text will be O(1) and return in ~0ms.
@lru_cache(maxsize=_CACHE_SIZE)
def _embed_one_cached(text: str) -> tuple[float, ...]: # a tuple of any length where every element is a float
    """
    Embed a single normalised text with LRU caching.

    LRU (Least Recently Used) is a fixed-size dict + doubly-linked list.
    Holds up to _CACHE_SIZE entries. When full, the entry unused longest
    is evicted — like 512 parking spots where the longest-idle car gets
    towed when a new one arrives.

    Storage: lives in the RAM of this Python process on the server.
    Not shared with pgvector, Redis, or any other worker process.
    Cleared on container restart — first call after restart pays full cost.

    Returns tuple (not list) because lru_cache requires a hashable return
    value — callers convert back to list[float].

    Cache key = the 'text' argument, which callers must normalise
    (lower + strip) so "What is malloc?" and "what is malloc?" share one slot.

    On cache miss: calls _embed_sync([text]) — CPU-bound, takes 100-300ms.
    On cache hit: returns the stored tuple — O(1), ~0ms.
    """
    return tuple(_embed_sync([text])[0]) # unwrap the single-item list and convert to tuple for caching


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
        result_tuple = await asyncio.to_thread(_embed_one_cached, key) #  Without asyncio.to_thread, FastEmbed would freeze the event loop for 100–300ms — no other request could be answered during that time. With it, the loop stays free while the CPU crunches numbers on a separate thread.

        return [list(result_tuple)]

    # Batch path: startup embeds all docs at once — bypass cache.
    return await asyncio.to_thread(_embed_sync, texts)
