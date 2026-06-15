 With 100 students at once, your app becomes a concurrency + quota management problem.

How it works right now

Each browser request hits your Go handler.
For each request, your server opens an outbound request to Gemini.
So 100 students can mean ~100 simultaneous open streams to Gemini.
Go can handle that concurrency, but Gemini quotas/rate limits usually become the bottleneck first.
What can go wrong at 100 concurrent users

Upstream throttling: Gemini returns 429 or slows down.
Too many open streams: memory and file descriptors increase.
Slow-client buildup: if some browsers read slowly, your server goroutines stay busy longer.
Unfair limiting: if you limit by IP only, many students behind one school NAT can be unfairly blocked.
Retry storms: failed clients retry immediately and make overload worse.

How to mitigate

Global concurrency cap for Gemini calls:
Use a semaphore/worker pool so only N active Gemini streams run at once.
Backpressure policy:
If cap reached, either queue briefly or fail fast with 429/503.
Per-user limits, not only per-IP:
Use user/session/API key identity; keep IP as secondary protection.
Proper timeouts:
Request timeout, outbound Gemini timeout, and server read/write/idle timeouts tuned for SSE.
Cancellation propagation:
When student closes tab, cancel context so outbound Gemini call stops immediately.
Circuit breaker behavior:
If Gemini starts failing repeatedly, short-circuit quickly for a window.
Observability:
Track active streams, queue length, upstream latency, 429 rate, error rate.
Cleanup in limiters:
Add TTL cleanup for limiter map entries so memory does not grow forever.

===

maxConcurrentGemini = 20 (start conservative).
Queue at most 50 waiting requests with max wait 2-3s.
If queue full, return 503 with “Server busy, retry in a few seconds”.
Per-user limit, e.g. 10 requests/min and daily cap.
Global upstream budget matching your real Gemini tier.
===

Go concurrency allows many students.
Capacity control decides how many are admitted.
Rate limiting decides fairness.
Timeouts and cancellation prevent stuck resources.