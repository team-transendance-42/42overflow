# Rate Limiting Implementation Plan for School 42 LLM Proxy

## Overview
Three-layer rate limiting for fair and sustainable access to free Gemini API:
1. **Per-Student Daily Quota** (persistent, resets UTC midnight)
2. **Per-Student Minute Limiter** (token bucket, burst protection)
3. **Global Concurrency Cap** (max simultaneous Gemini streams)

---

## Layer 1: Per-Student Daily Quota

### Data Model
Store quotas in a simple in-memory map or database.

```go
type StudentQuota struct {
    StudentID string    // User/session identifier
    Date      string    // "2026-04-05" format; reset at UTC midnight
    Count     int       // Requests made today
    MaxDaily  int       // Configured daily limit (e.g., 20)
}

var (
    dailyQuotas = make(map[string]*StudentQuota)  // key: "studentID|date"
    quotaMu     sync.Mutex
)
```

### Implementation Logic
```go
func checkDailyQuota(studentID string) (allowed bool, remaining int) {
    quotaMu.Lock()
    defer quotaMu.Unlock()
    
    today := time.Now().UTC().Format("2006-01-02")
    key := studentID + "|" + today
    
    // First request today: create quota
    if quota, ok := dailyQuotas[key]; !ok {
        dailyQuotas[key] = &StudentQuota{
            StudentID: studentID,
            Date:      today,
            Count:     0,
            MaxDaily:  20,  // Configurable default
        }
        return true, 19  // Allow, 19 remaining
    } else if quota.Count < quota.MaxDaily {
        quota.Count++
        return true, quota.MaxDaily - quota.Count
    }
    
    return false, 0  // Reject, no remaining
}
```

### Cleanup
Add background goroutine to clean old quota entries older than 3 days:
```go
func cleanOldQuotas() {
    ticker := time.NewTicker(1 * time.Hour)
    defer ticker.Stop()
    
    for range ticker.C {
        quotaMu.Lock()
        cutoff := time.Now().UTC().AddDate(0, 0, -3).Format("2006-01-02")
        for key := range dailyQuotas {
            parts := strings.Split(key, "|")
            if len(parts) == 2 && parts[1] < cutoff {
                delete(dailyQuotas, key)
            }
        }
        quotaMu.Unlock()
    }
}
```

---

## Layer 2: Per-Student Minute Limiter

### Implementation (extending existing ratelimit.go)
```go
var (
    minuteLimiters = make(map[string]*rate.Limiter)  // key: studentID
    mu              sync.Mutex
)

func getStudentLimiter(studentID string) *rate.Limiter {
    mu.Lock()
    defer mu.Unlock()
    
    if l, ok := minuteLimiters[studentID]; ok {
        return l
    }
    
    // 2 tokens/sec, burst 2 (~2 req/min, burst 2)
    l := rate.NewLimiter(rate.Limit(2.0/60.0), 2)  
    minuteLimiters[studentID] = l
    return l
}
```

### Cleanup with TTL
```go
type limiterEntry struct {
    limiter   *rate.Limiter
    lastUsed  time.Time
}

var (
    minuteLimitersWithTTL = make(map[string]*limiterEntry)
    mu                     sync.Mutex
)

func cleanStaleLimiters() {
    ticker := time.NewTicker(5 * time.Minute)
    defer ticker.Stop()
    
    for range ticker.C {
        mu.Lock()
        cutoff := time.Now().Add(-15 * time.Minute)  // Remove if unused > 15 min
        for id, entry := range minuteLimitersWithTTL {
            if entry.lastUsed.Before(cutoff) {
                delete(minuteLimitersWithTTL, id)
            }
        }
        mu.Unlock()
    }
}
```

---

## Layer 3: Global Concurrency Cap

### Semaphore Pattern
```go
var (
    activeLLMCalls = 0
    maxConcurrent   = 10  // Adjust based on Gemini free tier testing
    concurrentMu    sync.Mutex
)

func acquireSlot() (allowed bool) {
    concurrentMu.Lock()
    defer concurrentMu.Unlock()
    
    if activeLLMCalls < maxConcurrent {
        activeLLMCalls++
        return true
    }
    return false
}

func releaseSlot() {
    concurrentMu.Lock()
    activeLLMCalls--
    concurrentMu.Unlock()
}
```

### In Service Layer
```go
// In services/llm.go
func StreamLLM(ctx context.Context, req models.TextRequest) (<-chan string, error) {
    if !acquireSlot() {
        return nil, fmt.Errorf("server at capacity")
    }
    defer releaseSlot()
    
    // ... rest of StreamLLM
}
```

---

## Middleware Flow Order

Order matters for clean error handling and fairness:

```go
// In llm_server.go main()
router.Use(middleware.ErrorRecovery)      // 1. Catch panics
router.Use(middleware.StudentIdentity)    // 2. Extract/verify student ID
router.Use(middleware.DailyQuotaCheck)    // 3. Check daily quota (reject fast if over)
router.Use(middleware.MinuteLimiter)      // 4. Token bucket per student
// Global concurrency check happens in handlers, not middleware

router.HandleFunc("/api/ai-assist", handlers.GenerateText).Methods("POST", "OPTIONS")
```

### Middleware Implementation Examples

**StudentIdentity Middleware:**
```go
func StudentIdentity(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Extract from session, JWT, or header
        // For now, use IP behind NAT or mock
        studentID := r.Header.Get("X-Student-ID")
        if studentID == "" {
            studentID = getStudentFromIP(r.RemoteAddr)  // Fallback
        }
        
        // Store in context for downstream access
        ctx := context.WithValue(r.Context(), "studentID", studentID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

**DailyQuotaCheck Middleware:**
```go
func DailyQuotaCheck(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        studentID := r.Context().Value("studentID").(string)
        
        allowed, remaining := checkDailyQuota(studentID)
        if !allowed {
            w.Header().Set("Retry-After", "86400")  // Retry tomorrow
            http.Error(w, 
                fmt.Sprintf("daily quota exceeded; resets at UTC midnight"),
                http.StatusTooManyRequests)  // 429
            return
        }
        
        // Store remaining in context for response header
        ctx := context.WithValue(r.Context(), "quotaRemaining", remaining)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

**MinuteLimiter Middleware:**
```go
func MinuteLimiter(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        studentID := r.Context().Value("studentID").(string)
        limiter := getStudentLimiter(studentID)
        
        if !limiter.Allow() {
            w.Header().Set("Retry-After", "60")  // Retry in 1 minute
            http.Error(w,
                "rate limit exceeded; try again in 1 minute",
                http.StatusTooManyRequests)  // 429
            return
        }
        
        next.ServeHTTP(w, r)
    })
}
```

---

## Status Codes and Headers

### 429 Too Many Requests (Rate Limited)
```go
// Per-student minute limit exceeded
w.Header().Set("Retry-After", "60")
http.Error(w, "Rate limited. Try again in 60 seconds.", http.StatusTooManyRequests)

// Daily quota exhausted
w.Header().Set("Retry-After", "86400")
http.Error(w, "Daily quota exceeded. Resets at UTC midnight.", http.StatusTooManyRequests)
```

### 503 Service Unavailable (Overloaded)
```go
// Global capacity full or queue timeout
w.Header().Set("Retry-After", "10")
http.Error(w, "Server busy. Try again in 10 seconds.", http.StatusServiceUnavailable)
```

### Success Response Headers
```go
w.Header().Set("X-Daily-Quota-Remaining", fmt.Sprintf("%d", remaining))
w.Header().Set("X-Rate-Limit-Minute", "2")
w.Header().Set("X-Rate-Limit-Minute-Remaining", fmt.Sprintf("%d", burst-1))
w.Header().Set("X-Concurrent-Streams-Active", fmt.Sprintf("%d", activeLLMCalls))
```

---

## Default Constants (Production-Safe for Free Gemini)

```go
const (
    // Per-student per-minute: ~2 requests
    StudentMinuteLimitRate   = 2.0 / 60.0  // tokens/sec
    StudentMinuteLimitBurst  = 2            // tokens (allows short spike)
    
    // Per-student per-day: 20 requests
    StudentDailyLimit        = 20
    
    // Global concurrency: limit simultaneous Gemini streams
    MaxConcurrentGeminiCalls = 10
    
    // Queue timeout: how long to wait if server is busy
    QueueTimeoutSeconds      = 3
    
    // Limiter stale cleanup: remove bots/inactive users
    LimiterTTLMinutes        = 15
    QuotaTTLDays             = 3
)
```

---

## Error Handling Flow

```
Student Request
    ↓
[StudentIdentity] → Extract or assign student ID
    ↓
[DailyQuotaCheck] → Over daily limit? → Return 429 "quota expired"
    ↓
[MinuteLimiter] → Token bucket empty? → Return 429 "rate limit"
    ↓
Handler: GenerateText
    ↓
Ask StreamLLM:
    tryAcquireSlot() → Can't get slot? → Return 503 "busy"
    ↓
StreamLLM → Gemini → SSE stream
    ↓
Send success + headers (X-Daily-Quota-Remaining, etc.)
```

---

## Frontend UX Integration

### Display Remaining Quota
```javascript
// Parse response header
const remaining = response.headers.get('X-Daily-Quota-Remaining');
document.getElementById('quota-info').textContent = `${remaining} requests left today`;
```

### Handle 429 / 503 Errors
```javascript
if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    showError(`Too many requests. Retry in ${retryAfter} seconds.`);
    disableAskButton(parseInt(retryAfter) * 1000);
} else if (response.status === 503) {
    showError('Server busy. Please wait...');
    // Auto-retry with exponential backoff
}
```

---

## Testing Checklist

- [ ] Single student can make 2 requests/minute sustainably
- [ ] 3rd request in same minute is rejected with 429
- [ ] After 21st request in a day, all requests get 429 until next UTC midnight
- [ ] When 10 concurrent streams active, 11th request gets 503
- [ ] Retry-After headers are correct for each scenario
- [ ] Old quota entries cleaned up after 3 days
- [ ] Old limiters cleaned up after 15 minutes inactive
- [ ] Concurrent 100 requests distributes across capacity correctly
- [ ] Upstream Gemini 429 does not cause cascading failures

---

## Tuning for Your Measured Load

1. Test with actual Gemini free tier for 1 week.
2. Measure:
   - How many requests/day before 429
   - Response latency distribution
   - Concurrent stream limit before Gemini 429
3. Adjust constants based on data:
   - If too many 429s: raise StudentDailyLimit or StudentMinuteLimitRate
   - If Gemini returns 429: lower MaxConcurrentGeminiCalls
   - If queue times out: lower MaxConcurrentGeminiCalls or raise QueueTimeoutSeconds

---

## Next Steps

1. Choose how to extract student identity (session, JWT, IP+header fallback)
2. Implement middleware stack in order
3. Add cleanup goroutines to main()
4. Update frontend to parse Retry-After and quota headers
5. Deploy to staging and measure real Gemini behavior
6. Adjust constants based on observed limits
