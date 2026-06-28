Client request arrives
        │
        ▼
[1] Body size check         ← MaxBytesReader, reject >8KB
        │
        ▼
[2] Extract client key      ← RemoteAddr only (your fixed version)
        │
        ▼
[3] Daily token quota? per person     ← reject if over token budget
        │
        ▼
[4] Daily request quota?    ← reject if over 20/day: todo: better skip this step???
        │
        ▼
[5] Per-minute rate check   ← reject if >2/min
        │
        ▼
[6] Global rate check       ← reject if global cap hit
        │
        ▼
[7] Call Gemini             ← with retry + backoff on 429/5xx
        │
        ▼
[8] Stream or buffer        ← errors after this point go via SSE
        │
        ▼
[9] Record token usage      ← update entry.dailyTokens from response
        │
        ▼
Client receives response

========================================
Metric                    Limit (Free Tier)    Notes
RPD (Requests Per Day)     100 – 1,000       Resets at Midnight Pacific Time                                (PT). Limits vary significantly by model.
RPM (Requests Per Minute)     5 – 15        How many times you can hit the API                                         in 60 seconds.
TPM (Tokens Per Minute)    250,000 – 1,000,000   Total input + output tokens                                           allowed per minute.
Data PrivacyUsed for TrainingIn the Free Tier, Google may use your inputs/outputs to improve their models.



========================================
main -> router -> middleware -> handler -> llm.callGeminiWithRetry
main() only wires routes + middleware
RateLimiter does checks before Gemini
GenerateGeminiText calls llm.callGeminiWithRetry(...)
after Gemini returns, handler records token usage

========================================
two separate problems that both get called "rate limiting":

Your App
    │
    ├── 1. YOUR server limiting YOUR users
    │       "students can't spam the endpoint"
    │
    └── 2. Gemini/OpenAI limiting YOU
            "you can't spam their API"

Layer 1 — You limiting your users
This is what your current middleware does. The full list of things to consider:
What to track:
Per user:   requests/minute  (burst protection)
Per user:   requests/day     (quota fairness)
Global:     requests/minute  (protect your Gemini quota)
Per user:   tokens/day       (LLMs charge by token, not request)
Per user:   request body size (prompt stuffing)

======================================
TODO:
	// 1. Body size limit — a student sends a 1MB prompt, costs you money
// Add this BEFORE your rate limiter even runs:
r.Body = http.MaxBytesReader(w, r.Body, 8_000) // ~8KB max prompt
---
// 2. Token tracking — you currently count requests, not tokens.
// A student sends 1 request with 50k tokens = same as 1 "hello".
// Fix: read token count from Gemini response and track it per user.
tokensUsed := geminiResp.UsageMetadata.TotalTokenCount
entry.dailyTokens += tokensUsed
---
Layer 2 — Gemini limiting you (the hard part)
When Gemini returns HTTP 429, you have three choices:

429 received
     │
     ├── retry-after header present? ──yes──▶ wait exactly that long, retry once
     │
     ├── no header, first retry? ──────────▶ exponential backoff
     │
     └── retries exhausted? ────────────────▶ return error to user immediately
===================================
Think of rate limiter like a candy machine.

The machine has a bucket that can hold up to b candies.
At start, bucket is full.
Every time someone asks for candy, 1 candy is removed.
New candies are added slowly at speed r candies per second.
If no candy is left, you must wait or be denied.
That is exactly token bucket.

What r and b mean

r is the normal speed limit.
Example: r = 2 means about 2 requests each second forever.
b is burst size.
Example: b = 5 means you can do a quick burst of 5 requests at once before slowdown.

Three main actions

Allow:
Asks now, instantly.
If token exists, yes.
If not, no.
Good for quick reject with 429.

Reserve:
Asks now, gets answer like:
You can do it, but wait 700 ms.
Good when you want to schedule future action.

Wait:
Asks now and pauses until token is ready.
If context is canceled, it stops waiting.
Good for queue-like behavior.
===

Allow = try now, maybe fail
Reserve = book a future slot
Wait = stand in line
What zero value means

Empty limiter with no setup.
It blocks everything.
So you should create limiter with NewLimiter.

Why it says safe for many goroutines

Many users can hit same limiter at same time.
Package handles locking internally.
You do not need extra lock around Allow on same limiter object.
===

Tiny example
Suppose:

r = 10 tokens per second
b = 20
Then:

At start, 20 quick requests can pass.
After bucket empties, only about 10 requests each second can continue.
Extra requests get denied or delayed depending on method.
===

Stops student spam.
Lowers chance of Gemini 429.
Keeps app fair for all users.
Prevents sudden cost spikes.
Super simple rule to remember
Rate limiter is a speed governor:
You can run fast for a short burst, but average speed stays controlled.
=======================================================================================================
For an LLM proxy, rate limiting is not optional. It is the core control for fairness, cost, and uptime.
=======================================================================================================
Free Gemini is usually not suitable for sustained 500 requests per minute.
You should design for strict per-student quotas plus a global gateway cap.
Start conservative, measure real upstream behavior, then tune.
What 500 requests per minute really means

500 rpm is about 
8.3
8.3 requests per second.
If average stream lasts 15 to 25 seconds, required concurrency is large.
Using Little's Law: concurrency ≈ λ x W
With λ=8.3/s and W=20s, concurrency is about 166 166 active streams.
That is typically far above free-tier comfort.
So yes, 500 rpm at the app edge can be possible, but not if every request calls free Gemini directly in real time.
====

What policy is best for a school project
Use 3 layers at the same time.

*** Per-student limits: ***
Set both short-window and daily quota.
Example policy:
2 requests per minute
burst 2
20 requests per day
This is usually much better than 5 per day or 1 per hour.
5 per day is often too restrictive for learning.
1 per hour kills normal usage flow.

*** Global limits: ***
Protect server and upstream quota.
Example policy:
60 requests per minute global cap (meaining at the same 1 minute, only 30 students can be active if burst is 2)
burst 20
max in-flight Gemini streams 10 to 20 -> what  means that?

*** Overload behavior: ***
When full, fail fast with clear message.
Return 429 for user quota exceeded. ("Too many requests, try again later") -> todo; give how many requests per minute are allowed and when quota resets.
Return 503 when server queue/concurrency is full. ("Server busy, try again in a few seconds") ->todo;
Include Retry-After header.

*** What to key limits on ***
Primary key should be student identity, not IP.
IP-only is unfair in schools because many users share one NAT IP.
Keep IP limiter as backup abuse guard.
Store quotas in shared storage if you run multiple instances.

!!NB!!
Realistic free-tier expectation
Because free limits change by model/account/region, treat docs as starting point and verify empirically.
--

Caching repeated questions.-> is it easy to implement? Yes, you can add a simple in-memory cache with a map[string]string where key is the question and value is the answer. Before calling Gemini, check if the question exists in the cache. If yes, return cached answer. If no, call Gemini, store the result in cache, and return it. This can save tokens and speed up responses for common questions. Just be mindful of memory usage and cache eviction policy for a real app.

Asynchronous jobs for heavy requests.
Multi-model fallback routing.
Strong prompt/output limits to reduce duration. can we implement all these? Yes, but they add complexity. Caching is usually the easiest and most effective first step. Asynchronous jobs and multi-model routing require more architecture changes. Strong prompt/output limits can be implemented in the handler before calling Gemini, but you need to balance user experience with cost control. Start with caching and rate limiting, then consider adding more features as needed.
============================

Rate limiting design for robust LLM UI

Student quota:
Track count per student per day, reset at UTC midnight.
Minute limiter:
Token bucket for burst control.
Concurrency semaphore:
Cap active upstream streams.
Queue timeout:
Wait max 2 to 3 seconds, then 503.
Unified error contract:
Consistent JSON or SSE error events with code and retry hint.
User feedback:
Show remaining quota and cooldown messages in UI.
Observability:
Track 429 rate, 503 rate, queue wait, active streams, upstream latency, upstream 429.
=============================
Recommended starter numbers
=============================

Per student:
2 requests per minute: burst 2
20 per day: burst 20
Global: 40 to 60 requests per minute
burst 15 to 20
max concurrent upstream streams 12
Queue:
max queued 30
max wait 2 seconds
Prompt guard:
keep max prompt size bounded
How to tune after launch

Start strict for one week.
Measure rejected requests and latency.
If 429 is high but upstream stable, raise per-student daily limit first.
If upstream 429/5xx rises, lower global cap and concurrency.
Publish a transparent fair-use policy to students.

==============================================
TTL Cleanup - Prevents Unbounded Map Growth
==============================================

// In ratelimit.go, every student who asks a question creates an entry:
limiters[clientKey] = &ClientLimiter{...}

// Problem: If 1000 different students ask questions, the map grows to 1000.
// If server runs for months, limiters map could have 100,000+ entries.
// Each entry consumes memory → **unbounded growth = memory leak**

cleanupStaleLimiters() // Runs every 5 minutes, removes entries without activity for 30 min is curr fix: fter 30 minutes of inactivity, a student's entry is deleted, freeing memory.

=====================================================
Identity Spoofable - Secure Authentication with DB
=====================================================

// Anyone can send: X-Student-ID: 999
// Server trusts it blindly
func extractClientKey(r *http.Request) string {
    if sid := r.Header.Get("X-Student-ID"); sid != "" {
        return sid  // ❌ SPOOFABLE
    }
    return r.RemoteAddr
} not good securitywise: 

est practice with student DB auth:

Before rate limiter, add an authentication middleware that runs first:
// middleware/auth.go
package middleware

import (
    "context"
    "net/http"
)

// Middleware that validates JWT/session and sets authenticated user
func AuthRequired(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Extract JWT from Authorization header or session cookie
        token := r.Header.Get("Authorization") // or r.Cookie("session")
        
        // Verify token against your DB/auth provider
        userID, err := validateTokenWithDB(token)
        if err != nil {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        
        // Store verified identity in request context
        ctx := context.WithValue(r.Context(), "userID", userID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Then in ratelimit.go, extract from verified context (NOT headers):
func extractClientKey(r *http.Request) string {
    userID := r.Context().Value("userID")
    if userID != nil {
        return userID.(string)  // ✅ SECURE - verified by auth middleware
    }
    return r.RemoteAddr // Fallback to IP if no auth
}
Middleware chain in your main handler:

router.Use(middleware.AuthRequired)      // Run first: verify identity
router.Use(middleware.RateLimit)         // Run second: check limits using verified identity
router.HandleFunc("/api/ai-assist", handleAIRequest)
=============================================
In-Memory Only - Data Loss & Multi-Instance Problem
==============================================
Server restart:
  Map: {student_123: limiter_obj, student_456: limiter_obj}
       ↓ (server crashes)
  Map: {} (EMPTY - all data lost!)
  
Result: Any student can send unlimited requests for a few seconds until rate limiter state rebuilds.
Multi-instance problem (if you scale to 2+ containers):
Container A:                Container B:
{student_123: 1 req}      {student_123: 1 req}
{student_456: 2 req}      {student_456: 2 req}

Each container tracks independently. Student can send 2 reqs/min on A + 2 reqs/min on B = 4 req/min total.
Rate limit is BROKEN across instances.

Best practice fix: Use Redis (persistent + shared across containers)

// middleware/ratelimit_redis.go
package middleware

import (
    "context"
    "fmt"
    "github.com/redis/go-redis/v9"
    "net/http"
    "time"
)

var redisClient *redis.Client

func init() {
    redisClient = redis.NewClient(&redis.Options{
        Addr: "localhost:6379", // or from env
    })
}

func RateLimitRedis(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        userID := r.Context().Value("userID").(string)
        
        // Per-minute limit: 2 requests
        perMinKey := fmt.Sprintf("rl:min:%s", userID)
        count, err := redisClient.Incr(context.Background(), perMinKey).Val()
        if err != nil {
            http.Error(w, "Rate limiter error", http.StatusInternalServerError)
            return
        }
        
        // Set TTL on first request
        if count == 1 {
            redisClient.Expire(context.Background(), perMinKey, 1*time.Minute)
        }
        
        if count > 2 {
            w.Header().Set("Retry-After", "60")
            http.Error(w, "Rate limited", http.StatusTooManyRequests)
            return
        }
        
        // Per-day limit: 20 requests
        dayKey := fmt.Sprintf("rl:day:%s:%s", userID, time.Now().Format("2006-01-02"))
        dayCount, _ := redisClient.Incr(context.Background(), dayKey).Val()
        
        if dayCount == 1 {
            redisClient.Expire(context.Background(), dayKey, 24*time.Hour)
        }
        
        if dayCount > 20 {
            w.Header().Set("Retry-After", fmt.Sprintf("%d", secondsUntilMidnight()))
            http.Error(w, "Daily quota exceeded", http.StatusTooManyRequests)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}

// middleware/ratelimit_redis.go
package middleware

import (
    "context"
    "fmt"
    "github.com/redis/go-redis/v9"
    "net/http"
    "time"
)

var redisClient *redis.Client

func init() {
    redisClient = redis.NewClient(&redis.Options{
        Addr: "localhost:6379", // or from env
    })
}

func RateLimitRedis(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        userID := r.Context().Value("userID").(string)
        
        // Per-minute limit: 2 requests
        perMinKey := fmt.Sprintf("rl:min:%s", userID)
        count, err := redisClient.Incr(context.Background(), perMinKey).Val()
        if err != nil {
            http.Error(w, "Rate limiter error", http.StatusInternalServerError)
            return
        }
        
        // Set TTL on first request
        if count == 1 {
            redisClient.Expire(context.Background(), perMinKey, 1*time.Minute)
        }
        
        if count > 2 {
            w.Header().Set("Retry-After", "60")
            http.Error(w, "Rate limited", http.StatusTooManyRequests)
            return
        }
        
        // Per-day limit: 20 requests
        dayKey := fmt.Sprintf("rl:day:%s:%s", userID, time.Now().Format("2006-01-02"))
        dayCount, _ := redisClient.Incr(context.Background(), dayKey).Val()
        
        if dayCount == 1 {
            redisClient.Expire(context.Background(), dayKey, 24*time.Hour)
        }
        
        if dayCount > 20 {
            w.Header().Set("Retry-After", fmt.Sprintf("%d", secondsUntilMidnight()))
            http.Error(w, "Daily quota exceeded", http.StatusTooManyRequests)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}

================================================
###  No Global Protection - Add Concurrency Cap
================================================
You have 100 students, each with limit of 2 req/min.
They all ask at same time → 100 requests hit Gemini API simultaneously.
Gemini API overloads → 503 errors for everyone.

Individual limits don't protect the shared upstream service.

solution: global concurrency semaphore
// In handlers/handlers.go
package handlers

import (
    "sync"
    "net/http"
)

var (
    // Allow max 10 concurrent requests to Gemini
    concurrencySemaphore = make(chan struct{}, 10)
)

func HandleAIAssist(w http.ResponseWriter, r *http.Request) {
    // Acquire slot (blocking if all 10 are in use)
    concurrencySemaphore <- struct{}{}
    defer func() { <-concurrencySemaphore }()  // Release when done
    
    // Now call Gemini with at most 10 concurrent goroutines
    answer, err := services.CallGemini(r.Context(), prompt)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    // Stream response...
}

Channel with buffer size 10:
  concurrencySemaphore <- struct{}{}  // Block here if 10+ in use
  
Request 1-10:   Proceeds immediately (slots available)
Request 11:     BLOCKS until Request 1-10 finishes (then slot frees)
Request 12-100: Queue up, wait their turn

Result: Max 10 concurrent Gemini calls = protected upstream.

=============================================
OPTIONS/CORS Preflight - Explain & Your Case
=============================================
Browser sends OPTIONS request before POST:

POST /api/ai-assist with credentials
  ↓ (browser security check)
OPTIONS /api/ai-assist  ← Preflight to check CORS headers
  ↓
POST /api/ai-assist     ← Actual request

If your rate limiter counts OPTIONS requests:
  - Student hits preflight limit
  - Can't even send actual request
  - Rate limiter blocks unintentionally

  But to be safe, skip non-AI-assist endpoints:
  func RateLimitMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Skip rate limiting for non-AI routes
        if r.URL.Path != "/api/ai-assist" {
            next.ServeHTTP(w, r)
            return
        }
        
        // Skip rate limiting for OPTIONS (preflight)
        if r.Method == http.MethodOptions {
            next.ServeHTTP(w, r)
            return
        }
        
        // Apply rate limiting only to POST /api/ai-assist
        userID := r.Context().Value("userID").(string)
        // ... rate limit logic ...
        
        next.ServeHTTP(w, r)
    })
}
==================================
Add auth middleware (secure identity) ✅ Most urgent
Add global concurrency semaphore (protect Gemini) ✅ Prevents 503 cascades
Add Redis persistence (survive restarts + multi-instance) ⚠️ Medium priority
Skip OPTIONS / non-AI routes (clean rate limiting) ✅ Quick win
======================================

==========================
architecture:
========================
Browser (127.0.0.1:5173)
  ↓
Vite proxy (rewrites /api → localhost:8081)
  ↓
Middleware chain:
  1. ErrorRecovery
  2. RateLimiter    ← Applies to OPTIONS too!
  3. Handler (GenerateGeminiText)
  -------------------------------
Browser: OPTIONS /api/ai-assist (preflight)
  ↓ (vite proxy: /api/ai-assist → localhost:8081/api/ai-assist)
RateLimiter: "Student sent request" → counter++ (2/2)
  ↓
Handler: if Method==OPTIONS return 204
  ↓
Result: NOW when actual POST comes, student is at 2/2 limit!
        Preflight wasted 1 slot.
        =========================
        What is Vite?
Vite is a development build tool for frontend projects. It:

Bundles your Svelte/TypeScript code
Serves it on http://127.0.0.1:5173 (dev server)
Hot-reloads when you edit files
Has a built-in dev proxy to redirect API calls

Is This Best Practice?
For development? YES, standard practice

All Node.js/Vite projects use dev proxies
Keeps frontend and backend separate during development
Simulates production-like API calls

For production? ⚠️ NO, need real reverse proxy

In production, you should have:

Vite builds a static .svelte-kit/build/ folder (HTML/JS/CSS)
A real reverse proxy (Nginx, Apache, or Docker) serves:
Static files from .svelte-kit/build/
API requests forwarded to Go backend on same domain

prod architecture:
Client (browser)
  ↓
Nginx (reverse proxy on port 80/443)
  ├─ GET /          → Serve SvelteKit HTML
  ├─ GET /js/...    → Serve SvelteKit JavaScript
  └─ POST /api/...  → Forward to Go backend on port 8081

  Quick answer: You have 1 proxy (Vite), it's correctly configured for development. For production, you'll need to add a real Nginx/Docker reverse proxy, but that's a separate deployment step.

  In production with a proper reverse proxy (Nginx), OPTIONS requests typically DON'T reach your backend at all.
  Browser: OPTIONS /api/ai-assist
  ↓
Nginx (reverse proxy)
  ├─ Sees it's OPTIONS
  ├─ Checks CORS headers in config
  ├─ Sends back 200 OK directly
  └─ Never forwards to Go backend!

Browser: POST /api/ai-assist (actual request)
  ↓
Nginx: Forwards to Go backend
  ↓
Rate limiter counts this
=============================
Your Nginx config would look like:

server {
    listen 80;
    
    location /api/ {
        # Nginx handles OPTIONS automatically
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type';
            return 204;
        }
        
        # Only POST requests reach backend
        proxy_pass http://localhost:8081;
    }
}
===============================
Why You NEED Nginx (in production)?
Your current development setup (works fine):
Browser: http://127.0.0.1:5173
  ↓ (Vite proxy: /api → :8081)
Go server: http://127.0.0.1:8081

Production setup (you'll need Nginx):

Browser: https://example.com
  ↓
Nginx (on port 443)
  ├─ GET /           → Serve SvelteKit static files
  ├─ GET /js/*       → Serve JavaScript
  └─ POST /api/*     → Forward to Go server on :8081 (internal, not exposed)

Result:
  ✓ Single domain (no CORS issues)
  ✓ Single port (80/443)
  ✓ Handle SSL/TLS certificates
  ✓ Go server stays internal (port 8081 not exposed to internet)

