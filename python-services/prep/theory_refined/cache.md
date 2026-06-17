llm-system-interface/services/cache.go — a plain Go map[string]ragCacheEntry] protected by a sync.Mutex. It
  lives entirely in the llm-server container's heap. No Redis, no disk, no file.

  [user question] → ragCacheGet() → hit? → serve immediately, skip Python RAG + Ollama entirely
                                  → miss? → retrieve → generate → ragCacheSet() → serve
==============================
  TTL

  const ragCacheTTL = time.Hour  // 1 hour, hardcoded

  Lazy expiry — no background goroutine. Expired entries are only evicted when someone tries to read them. If you
  write 500 entries and never re-read them, they sit in memory until the process dies.

  No max size, no LRU eviction. In theory the map grows unbounded. At ~2KB per answer × 1000 questions = ~2MB, so
  in practice not a concern, but worth knowing.
=================================
  Consistency

  - Thread-safe: mutex on every Get and Set, no races
  - Within TTL: if the underlying RAG data changes (you add new seed QA pairs), the cache serves the stale answer
  for up to 1 hour
  - Across restarts: cache is wiped — every docker compose restart llm-server is a full cache flush
  - Across instances: not shared — if you ran 2 llm-server replicas, each would have its own independent cache
================================
 How to clear

  # Nuclear: clear everything
  docker compose restart llm-server

 todo: /cache/clear endpoint. 
 todo;   - The cache is checked before the relevance gate — so if a question was previously answered and the gate
  thresholds were different then, you still get the old cached answer.
---
  model QAPair {
    id         Int      @id @default(autoincrement())
    question   String   @unique
    answer     String
    topic      String
    difficulty String?
    source     String?
    tags       String[]
    createdAt  DateTime @default(now())
    updatedAt  DateTime @updatedAt
  }
difficulty and source: why we need them? it looks like we dont use this?
====
todo: add all pwds and keys in .secrets/

