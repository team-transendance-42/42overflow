
  The concrete benefits of using go PROS:
  ========================
  the concurrency-safe cache (real, high-value),
  the goroutine-based streaming(clean),
  low RAM overhead (real but secondary). 
  
  CONS:
  ========================
  The cost is cross-language maintenance for a service boundary that Python + FastAPI could have
  handled with near-identical performance.
  ======================================
  ragCache in services/cache.go — a plain Go map[string]ragCacheEntry that lives in the process's RAM, inside the Go container. Nothing
  external (no Redis, no file).

  Key = normalized question (strings.ToLower + TrimSpace).
  Value = the full LLM answer string + an expiry timestamp.

  "what is malloc" → { answer: "malloc allocates...", expiresAt: +1h }

  Rules:
  - TTL = 1 hour. After that the entry is deleted on next read.
  - Max 500 entries. When full, oldest entry is evicted (FIFO — not LRU).
  - "No info" answers are never cached, so a future sync that adds real data isn't blocked.
  - Partial answers (client disconnected mid-stream) are never cached — we'd serve a truncated answer to the next user for 1h.

  The real benefit: when two students ask the same question within an hour, the entire RAG pipeline is skipped — no Python call, no ChromaDB, no
  Ollama. The cached answer is pushed into a channel and returned immediately.
=================================
Concurrency — why does it matter here?

  The problem Go solves: Go's map panics at runtime if two goroutines access it simultaneously — one writing, one reading. Python's dict doesn't
  panic because the GIL serializes everything by default.

  !!Our Go container handles each HTTP request as its own goroutine.!! If 20 students submit questions at the same time, we have 20 goroutines all
  potentially calling ragCacheGet at once. Without protection: crash.

  The solution is sync.RWMutex — a reader-writer lock:

  ragCacheMu.RLock()    // read lock — many goroutines can hold this simultaneously
  e, ok := ragCache[key]
  ragCacheMu.RUnlock()  // release

  // ... only on write:
  ragCacheMu.Lock()     // exclusive — everyone else waits
  ragCache[key] = ...
  ragCacheMu.Unlock()

  Why the split matters:
  Reads are cheap and frequent. Multiple goroutines can read the cache at the exact same moment — RLock allows that. Only when writing do other
  goroutines have to wait. In Python, the GIL would serialize all of this anyway — we get the same correctness but lose true parallelism on
  CPU-bound work.

  There's also a subtle double-check pattern in our expiry code — when a goroutine upgrades from RLock to Lock to delete an expired entry, it
  re-checks the entry inside the write lock, because another goroutine might have already deleted it in the tiny gap between the two locks.
  ============================
   Goroutine-based streaming — why better than Python?

  In the code the flow is:

  HTTP handler goroutine
      └─ calls StreamRagAnswer()
           └─ spawns goroutine: readOllamaToChannel(ctx, resp, rawCh)
                └─ reads Ollama JSON stream token by token → pushes to rawCh
           └─ spawns goroutine: accumulates + maybe caches → forwards to outCh
      └─ streamSSE() reads outCh → flushes each chunk as SSE to browser

  Two goroutines are doing real work simultaneously: one is reading from Ollama's TCP stream, the other is writing to the client. They're
  connected by a channel — a typed pipe that automatically blocks when the receiver isn't ready. No polling, no callbacks.

  In Python + FastAPI the equivalent is:
  async def stream():
      async for chunk in ollama_response.aiter_lines():
          yield chunk

  This works and is clean. But:

  ┌───────────────────────────┬────────────────────────────────────────────────┬─────────────────────────────────────────────────────┐
  │                           │                 Go goroutines                  │                    Python async                     │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Execution model           │ OS-scheduled, truly parallel on multiple cores │ Single-threaded event loop, cooperative             │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Blocking I/O              │ Any goroutine can block, others keep running   │ A blocking call in async code stalls the whole loop │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Accumulation + forwarding │ Two goroutines, both doing work                │ Two coroutines, but only one runs at a time         │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Backpressure              │ Channel blocks the producer naturally          │ asyncio.Queue or manual flow control                │
  └───────────────────────────┴────────────────────────────────────────────────┴─────────────────────────────────────────────────────┘

  The practical difference for our case: when Ollama is slow (generating tokens) and the client is also slow (bad connection), Go handles the
  mismatch cleanly — the channel just blocks the producer goroutine, no event loop stall. In Python, if we have a synchronous-ish operation mixed
  in (like the retry logic or the JSON accumulation), we have to be careful about blocking the event loop.

  The caching goroutine is particularly clean — it accumulates the full answer in a strings.Builder while simultaneously forwarding each chunk,
  then caches at the end only if the context wasn't cancelled. In Python we'd need asyncio.gather or a background task to do the same thing
  without blocking the stream.
  ===============================
  Goroutine-based streaming — why better than Python?

  In our code the flow is:

  HTTP handler goroutine
      └─ calls StreamRagAnswer()
           └─ spawns goroutine: readOllamaToChannel(ctx, resp, rawCh)
                └─ reads Ollama JSON stream token by token → pushes to rawCh
           └─ spawns goroutine: accumulates + maybe caches → forwards to outCh
      └─ streamSSE() reads outCh → flushes each chunk as SSE to browser

  Two goroutines are doing real work simultaneously: one is reading from Ollama's TCP stream, the other is writing to the client. They're
  connected by a channel — a typed pipe that automatically blocks when the receiver isn't ready. No polling, no callbacks.

  In Python + FastAPI the equivalent is:
  async def stream():
      async for chunk in ollama_response.aiter_lines():
          yield chunk

  This works and is clean. But:

  ┌───────────────────────────┬────────────────────────────────────────────────┬─────────────────────────────────────────────────────┐
  │                           │                 Go goroutines                  │                    Python async                     │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Execution model           │ OS-scheduled, truly parallel on multiple cores │ Single-threaded event loop, cooperative             │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Blocking I/O              │ Any goroutine can block, others keep running   │ A blocking call in async code stalls the whole loop │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Accumulation + forwarding │ Two goroutines, both doing work                │ Two coroutines, but only one runs at a time         │
  ├───────────────────────────┼────────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ Backpressure              │ Channel blocks the producer naturally          │ asyncio.Queue or manual flow control                │
  └───────────────────────────┴────────────────────────────────────────────────┴─────────────────────────────────────────────────────┘

  The practical difference for our case: when Ollama is slow (generating tokens) and the client is also slow (bad connection), Go handles the
  mismatch cleanly — the channel just blocks the producer goroutine, no event loop stall. In Python, if we have a synchronous-ish operation mixed
  in (like the retry logic or the JSON accumulation), we have to be careful about blocking the event loop.

  The caching goroutine is particularly clean — it accumulates the full answer in a strings.Builder while simultaneously forwarding each chunk,
  then caches at the end only if the context wasn't cancelled. In Python you'd need asyncio.gather or a background task to do the same thing
  without blocking the stream.
========================================================================================
  Low RAM overhead — what is it?

  RAM overhead = memory our process uses before it does any real work.

  ┌────────────────────────────┬────────────────────────┐
  │          Runtime           │ Base RAM just to start │
  ├────────────────────────────┼────────────────────────┤
  │ Python + FastAPI + uvicorn │ ~60–90 MB              │
  ├────────────────────────────┼────────────────────────┤
  │ Go binary                  │ ~8–15 MB               │
  └────────────────────────────┴────────────────────────┘

  Why? Python loads the interpreter, the entire standard library, FastAPI, Pydantic, uvicorn, starlette — all before the first request. Go
  compiles to a single static binary that includes only what our code uses.

  Per-request cost:
  - Go spawns a goroutine: ~2–8 KB of stack, grows on demand.
  - Python with async: lower than threads (~256 KB each), but each async task + uvicorn worker has overhead.
  - Python with threads (if you used sync FastAPI): ~1 MB per thread.

  For our case specifically: our Go service is pure I/O — it waits on Python RAG, waits on Ollama, forwards chunks. The RAM saved is real but
  you're right that it's secondary — you're not running thousands of concurrent connections where it would matter enormously. The cache
  correctness (RWMutex) and the streaming cleanness (channels) are the real wins.

  ---
  Summary:
  The cache is in-RAM Go map, guarded by RWMutex so concurrent goroutines don't corrupt it. Goroutine streaming is cleaner than Python async
  because the producer and consumer are truly independent, connected by a channel that handles backpressure automatically. Low RAM is real but not
  the deciding factor at our scale.
  =================================
services/cache.go only caches RAG answers — the final text that Ollama produced after the full pipeline ran. The regular chat endpoint
  (/api/chat) has no cache at all.
=================================
  Where exactly is the Go cache stored?

  It lives in the heap memory of the Go process, inside the llm-server Docker container, on the school's server machine.

  Browser (anyone's machine)
      │  HTTP/SSE
      ▼
   server machine (physical hardware)
      └─ Docker runtime
           └─ llm-server container   ← ragCache lives HERE, in RAM
                └─ Go process heap
                     └─ map[string]ragCacheEntry  ← this is it

  Not in the browser — the browser never touches it, it's opaque.
  Not on disk — it's a plain Go map, no file, no SQLite.
  Not shared — if the container restarts, the cache is gone. Next request = cold miss.
  Scope = one container instance — if we ever ran two llm-server containers (we don't now), each would have its own separate cache.
=======================================
What is the Python qa_cache?

  It's this line in indexer.py:
  qa_cache: dict = {"qa_pairs": []}

  It stores the raw list of Q&A pairs (from seed.json + Postgres) that were loaded at startup. It's not a query-result cache. It's a module-level
  variable used to hold the dataset so the admin /sync-chroma endpoint can reload without re-hitting the DB for every call.

  ---
  4. The real Python "cache" — app.state

  The actual search structures that Python keeps in memory are stored on app.state (FastAPI's per-app state object, also in Python process RAM):

  ┌───────────────────────┬───────────────────────────────────────────────────────┐
  │         What          │                      What it is                       │
  ├───────────────────────┼───────────────────────────────────────────────────────┤
  │ app.state.bm25        │ BM25 keyword index — built from all Q&A texts         │
  ├───────────────────────┼───────────────────────────────────────────────────────┤
  │ app.state.numpy_index │ Dense vector matrix — all embeddings as a numpy array │
  ├───────────────────────┼───────────────────────────────────────────────────────┤
  │ app.state.id_to_text  │ {doc_id → full text} — lookup by ID                   │
  ├───────────────────────┼───────────────────────────────────────────────────────┤
  │ app.state.id_to_topic │ {doc_id → topic name}                                 │
  ├───────────────────────┼───────────────────────────────────────────────────────┤
  │ app.state.centroids   │ {topic → centroid vector} — for topic detection       │
  └───────────────────────┴───────────────────────────────────────────────────────┘

  These are built once at startup from ChromaDB + seed, and rebuilt when /admin/sync-chroma is called. ChromaDB itself is persistent on disk
  (Docker volume) and is used only for storing embeddings between restarts — at query time your code bypasses ChromaDB and uses NumpyIndex
  directly (50–150ms network call replaced by 0.05ms in-process multiply).
  ================================
  - Go cache = final LLM answers, keyed by question, in Go process RAM, lives as long as the container runs.
  - Python qa_cache = raw Q&A pair list in Python process RAM, used for reindexing.
  - Python app.state.* = the live search indexes (BM25, NumpyIndex, centroids) in Python process RAM, built at startup.
  - ChromaDB = persistent embedding storage on disk, used for syncing — not for queries anymore.
