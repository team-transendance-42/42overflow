dentity-based limiting:
Use user/session/API key as primary limiter key, IP as fallback.
Two-level limits:
Per-user + global system cap.
Concurrency limiting:
Cap in-flight Gemini requests (separate from request rate).
Timeouts:
Request timeout, outbound Gemini timeout, and streaming-safe server timeouts.
Retry policy:
Retry only transient failures with jitter; never blind retries on 429.
Circuit breaker:
If Gemini is failing repeatedly, fail fast briefly to protect your server.
Fair queue:
Short queue with max wait; return 503 when overloaded.
Observability:
Track active streams, 429 count, Gemini latency, error rates, queue depth.
Practical policy for 100 students

Per-user: 12 req/min, burst 4.
Per-IP fallback: 60 req/min, burst 20.
Global in-flight Gemini: 20 to 30 streams.
Queue wait max: 2 to 3 seconds.
Daily budget per user/class to avoid quota exhaustion.
UI behavior for robust UX

On 429: show “Too many requests, try again in X seconds.”
On overload 503: show “Server busy, retry shortly.”
Disable submit while one stream active per chat tab.
Surface retry guidance, not raw backend errors.
Keep streaming partial output if possible, then graceful end message.
If you want, next step I can implement the first hardening pass directly in ratelimit.go: stable client key extraction, TTL cleanup for limiter map, and configurable limits.