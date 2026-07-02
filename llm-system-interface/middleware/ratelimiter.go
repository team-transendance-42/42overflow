package middleware

import (
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	"golang.org/x/time/rate" // rate.newLimiter
)

type limiterEntry struct {
	limiter  *rate.Limiter
	dayUTC   string
	dailyCnt int
	lastSeen time.Time
}

/*
* limiter:
Imagine a bucket that holds up to 5 tokens.
One request needs 1 token.
Tokens are added continuously at 10/60 tokens per second (about 1 token every 6 seconds).
If a request arrives and bucket has at least 1 token:
request is allowed, 1 token is removed.
If no token is available:request is denied 429
globalLimiter is one shared object for the whole process.
Every request hits this check first.
Then per-client limiter runs
*/
var (
	mu            sync.Mutex
	limiters      = make(map[string]*limiterEntry)            // kyes r str, val=ptr to limiterentry
	globalLimiter = rate.NewLimiter(rate.Limit(10.0/60.0), 5) // token bucket algorithm:Average: 10 requests/minute across all clients; Burst: up to 5 immediate requests before throttling starts
)

const (
	perStudentRateLimit = rate.Limit(5.0 / 60.0)
	perStudentBurst     = 2
	perStudentDailyMax  = 20
	limiterTTL          = 30 * time.Minute // remove inactive limiter entries after this idle time
	cleanupInterval     = 5 * time.Minute  //  how often the janitor wakes up
	maxLimiters         = 10_000           // safety cap: prevents unbounded map growth from bot/fake IDs -> used
)

func secondsB4UTCMidnight(now time.Time) int {
	midnight := time.Date(now.Year(), now.Month(), now.Day()+1, 0, 0, 0, 0, time.UTC)
	return int(time.Until(midnight).Seconds())
}

/*
looks up or creates a per-client rate limiter entry by key (IP address)
Lock — acquires the mutex since limiters map is shared across goroutines.
Lookup — if an entry for this key already exists, updates lastSeen and returns it.
Cap check — if the map has hit maxLimiters (10,000), returns false to signal "map full" — bot protection against fake IDs exhausting memory.
*/
func getLimiter(key string) (*limiterEntry, bool) {
	mu.Lock()
	defer mu.Unlock()

	now := time.Now().UTC()
	today := now.Format("2006-01-02")

	if entry, ok := limiters[key]; ok {
		entry.lastSeen = now
		return entry, true
	}

	// cap map size to prevent memory exhaustion from bots rotating fake student IDs
	if len(limiters) >= maxLimiters {
		return nil, false
	}

	entry := &limiterEntry{
		limiter:  rate.NewLimiter(perStudentRateLimit, perStudentBurst),
		dayUTC:   today,
		dailyCnt: 0,
		lastSeen: now,
	}
	limiters[key] = entry
	return entry, true
}

// extractClientKey returns a rate-limit bucket key for this request.
// Prefers X-User-ID (set by SvelteKit after session auth) — unfakeable because it comes
// from a verified session, not a client-controlled header. Falls back to IP so the
// /healthz probe and any direct calls still work.
func extractClientKey(r *http.Request) string {
	if uid := strings.TrimSpace(r.Header.Get("X-User-ID")); uid != "" {
		return "user:" + uid
	}

	if xff := strings.TrimSpace(r.Header.Get("X-Forwarded-For")); xff != "" {
		// X-Forwarded-For may contain a comma-separated chain: client,proxy1,proxy2
		first := strings.TrimSpace(strings.Split(xff, ",")[0])
		if ip := net.ParseIP(first); ip != nil {
			return "ip:" + ip.String()
		}
	}

	if xri := strings.TrimSpace(r.Header.Get("X-Real-IP")); xri != "" {
		if ip := net.ParseIP(xri); ip != nil {
			return "ip:" + ip.String()
		}
	}

	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return "ip:" + strings.TrimSpace(r.RemoteAddr)
	}
	return "ip:" + host
}

/*
*
lowercase name = private to that package
uppercase name = exported
deletes idle entries for longer than limiterTTL
*/
func StartCleanup() {
	go func() {
		for {
			time.Sleep(cleanupInterval)

			mu.Lock()
			now := time.Now().UTC()

			for key, entry := range limiters {
				if now.Sub(entry.lastSeen) > limiterTTL { // subtr
					delete(limiters, key)
				}
			}

			mu.Unlock()
		}
	}()
}

// RateLimiter is an HTTP middleware that enforces two tiers of rate limiting:
//   - Global: shared token bucket across all clients (10 req/min, burst 5) to protect upstream API quota.
//   - Per-client: individual token bucket keyed by IP (5 req/min, burst 2) with a daily cap of 20 requests.
//
// Sets X-RateLimit-* response headers and returns 429 on limit breach.
func RateLimiter(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Health check probes must never consume rate-limit tokens.
		// Docker hits /healthz every 10s from 127.0.0.1; the per-student
		// limit (5/min) would eventually deplete that bucket → 429 →
		// container marked unhealthy even while serving requests fine.
		if r.URL.Path == "/healthz" {
			next.ServeHTTP(w, r)
			return
		}

		// --- per-student limiter ---
		entry, ok := getLimiter(extractClientKey(r))
		if !ok {
			// map is full — too many unique IDs (likely a bot attack)
			http.Error(w, "Server busy", http.StatusServiceUnavailable)
			return
		}

		now := time.Now().UTC()

		// set base quota headers before any rejection so client always knows the limits
		w.Header().Set("X-RateLimit-Minute", "5")
		w.Header().Set("X-RateLimit-Day", strconv.Itoa(perStudentDailyMax))

		// No defer mu.Unlock() here — mu must be released BEFORE calling next.ServeHTTP.
		// Using defer would hold the lock for the entire downstream handler, serialising all requests.
		// Each return path unlocks explicitly; the happy path unlocks before ServeHTTP.
		mu.Lock()
		// re-check day rollover inside the lock (getLimiter may have run slightly earlier)
		today := now.Format("2006-01-02")
		if entry.dayUTC != today {
			entry.dayUTC = today
			entry.dailyCnt = 0
		}

		if entry.dailyCnt >= perStudentDailyMax {
			w.Header().Set("X-RateLimit-Day-Remaining", "0")
			w.Header().Set("Retry-After", strconv.Itoa(secondsB4UTCMidnight(now)))
			mu.Unlock()
			http.Error(w, "Daily quota exceeded (20/day)", http.StatusTooManyRequests)
			return
		}

		// --- per-minute rate check ---
		if !entry.limiter.Allow() {
			remaining := perStudentDailyMax - entry.dailyCnt
			w.Header().Set("X-RateLimit-Day-Remaining", strconv.Itoa(remaining))
			w.Header().Set("Retry-After", "30")
			mu.Unlock()
			http.Error(w, "Rate limit exceeded (5/min)", http.StatusTooManyRequests)
			return
		}

		// Global cap checked after per-student gates: over-quota/throttled requests must not
		// consume shared API quota tokens. rate.Limiter is goroutine-safe so calling inside mu is fine.
		if !globalLimiter.Allow() {
			mu.Unlock()
			http.Error(w, "Server busy, try again shortly", http.StatusTooManyRequests)
			return
		}

		entry.dailyCnt++
		remaining := perStudentDailyMax - entry.dailyCnt
		w.Header().Set("X-RateLimit-Day-Remaining", strconv.Itoa(remaining))

		mu.Unlock()
		// call next handler
		next.ServeHTTP(w, r)
	})
}
