
  Rate limiting (middleware/ratelimiter.go):
  - Global: token bucket, 10 req/min, burst 5 — protects the upstream Gemini API quota
  - Per-client: keyed by X-User-ID (verified session) or fallback IP; 5 req/min, burst 2, daily cap of 20
  - Retry-After and X-RateLimit-* headers set on 429 responses
  - Memory-safe: map capped at 10,000 entries; idle entries cleaned up every 5 minutes

  Error handling:
  - ErrorRecovery middleware: catches panics, returns 500 (middleware/errors.go:14)
  - InternalSecret middleware: rejects requests without X-Internal-Secret
  - withRetry (services/retry.go:28): 3 retries with exponential backoff on 429, 503, 504 from upstream
  - Input validation: 20,000-char total message size limit, prompt sanitization, empty-prompt check
  - Proper HTTP codes: 400, 413, 429, 502, 503 — all used correctly
  - Semaphore queues for Ollama and RAG (ollamaQueue, ragQueue) with 30-second timeout — prevents CPU overload without hanging clients
