 @lru_cache is a decorator — so first, decorators, then LRU cache itself.

 Decorators — the @ syntax

  A decorator is just a function that wraps another function. The @ is syntactic sugar:

  @lru_cache(maxsize=512)
  def _embed_one_cached(text: str): ...

  # exactly the same as:
  def _embed_one_cached(text: str): ...
  _embed_one_cached = lru_cache(maxsize=512)(_embed_one_cached)

  So lru_cache receives your function, returns a new function with caching behavior bolted on. Your
  code calls the wrapper, not the original.
  =========================
    LRU = Least Recently Used — a cache eviction strategy.

  You have a fixed number of slots (512 here). When it's full and a new item arrives, it evicts the
  item that was used least recently — the one that's been sitting untouched the longest.

  Cache (maxsize=3), calls: A, B, C, D, B

  After A:  [A]
  After B:  [A, B]
  After C:  [A, B, C]   ← full
  After D:  [B, C, D]   ← A evicted (oldest unused)
  After B:  [C, D, B]   ← B was hit, moves to "most recent"

  The intuition: if you used something recently, you're likely to use it again. Evict the forgotten
  things.
==========================
The cache key

  lru_cache uses the function arguments as the key. Arguments must be hashable — that's why strings
  work (strings are hashable in Python) and lists don't (lists are mutable, not hashable).

  That's also why _embed_one_cached returns a tuple, not a list:

  @lru_cache(maxsize=_CACHE_SIZE)
  def _embed_one_cached(text: str) -> tuple[float, ...]:
      return tuple(_embed_sync([text])[0])
---

lru_cache stores the return value too — it must be retrievable later. Technically return values don't
  need to be hashable (they're just stored, not used as keys), but returning a tuple signals clearly
  that this is immutable/cached data. The caller converts back: list(result_tuple).

  ---
  Why normalize the key before calling it

  key = texts[0].lower().strip()
  result_tuple = await asyncio.to_thread(_embed_one_cached, key)

  "What is malloc?" and "what is malloc?" are different strings → different dict keys → cache miss even
  though they'd produce identical embeddings. Normalizing first means they share one slot. The model
  also sees consistent input.

  ---
  Thread safety

  lru_cache is thread-safe in CPython. It uses:
  - The GIL (Global Interpreter Lock) — only one thread runs Python bytecode at a time
  - An internal lock for the linked list mutations

  So two threads calling _embed_one_cached("malloc") simultaneously: one will compute, the other will
  wait and get the cached result. No corruption, no double-compute in practice.
  ---
  ---
  Memory cost

  512 slots × 768 floats × 4 bytes (float32) = ~1.5 MB

  Negligible. The model itself is ~2 GB in RAM — the cache is rounding error.
----
  ├────────────────┼────────────────────────────────────────────────────────┤
  │ LRU policy     │ evict least-recently-used when full                    │
  ├────────────────┼────────────────────────────────────────────────────────┤
  │ data structure │ dict (O(1) lookup) + doubly-linked list (O(1) recency) │
  ├────────────────┼────────────────────────────────────────────────────────┤
  │ cache key      │ the function arguments — must be hashable              │
  ├────────────────┼────────────────────────────────────────────────────────┤
  │ thread safety  │ GIL + internal lock                                    │
  ├────────────────┼────────────────────────────────────────────────────────┤
  │ .cache_clear() │ method added by lru_cache to wipe all slots            │
  ├────────────────┼────────────────────────────────────────────────────────┤
  │ cost here      │ 1.5 MB RAM, repeated queries go from 200ms → 0ms       │



