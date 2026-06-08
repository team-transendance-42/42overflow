 Step 4 — LRU cache on question embeddings

  What we do: Add @lru_cache(maxsize=512) to a single-text embedding
  function. embed_texts([question]) (the query-time path) checks the
  cache first. Cache hit → ~0ms. Cache miss → normal fastembed call
  (~100–300ms on CPU).

  Theory — LRU (Least Recently Used) cache: Python's functools.lru_cache
   is an O(1) dict + doubly-linked list. On hit: one dict lookup, one
  list reorder — negligible. On eviction: the least-recently-used entry
  is dropped when maxsize is reached. lru_cache is thread-safe under the
   GIL and works correctly across asyncio.to_thread calls.

  Why only single-text path, not batch: Startup embeds 200 unique docs
  in one batch call — lru_cache can't key a list[str] (not hashable),
  and 200 unique questions would all miss anyway. At query time the call
   is always embed_texts([one_question]) — exactly the case the cache is
   designed for.

  Pros: Repeated questions (common in a 42-school context: "what is
  norminette?", "how does malloc work?") skip the entire fastembed call.
   No new dependency — functools is stdlib. 512 slots × 768 floats × 4
  bytes ≈ 1.5MB RAM (negligible).

  Cons: Cache is process-local — clears on restart, not shared between
  workers. Novel questions (first time asked) get no benefit. Multi-text
   batch calls bypass the cache.

  Edge cases:
  - Cache key is lowercased + stripped — "What is malloc?" and "what is
  malloc?" share one slot; the normalized form is what gets embedded
  (consistent)
  - Thread safety: lru_cache internal lock + GIL — safe under
  asyncio.to_thread
  - asyncio.to_thread overhead on cache hit ~0.01ms — negligible vs
  100–300ms saved
  - cache_clear() must be called between tests to prevent cross-test
  contamination