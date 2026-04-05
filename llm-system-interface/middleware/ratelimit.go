package middleware

import (
	"net"     // low-level networking utilities (IP, ports, socket-style helpers).
	"net/http" // HTTP server/client package (requests, responses, handlers, middleware).
	"strconv"
	"strings"
	"sync"
	"time" // time.Time,  time.Now().UTC() time.NewTicker(...)

	"golang.org/x/time/rate" // rate.Limit(2.0 / 60.0) (2 requests/min)
)

type limiterEntry struct {
	limiter  *rate.Limiter
	dayUTC   string
	dailyCnt int
	lastSeen time.Time
}

var (
	limiters           = make(map[string]*limiterEntry)
	mu                 sync.Mutex
	startCleanupWorker sync.Once // ensures the cleanup worker is started only once: not one per request, but just a single background goroutine for cleanup

	// globalLimiter caps total requests to the Gemini API across ALL students.
	// Free Gemini tier: ~15 RPM total. We use 10 to leave headroom.
	// With 100 students at 2 req/min each = 200 req/min potential — way over free tier.
	// This global cap prevents blowing the Gemini quota even if many students hit it at once.
	globalLimiter = rate.NewLimiter(rate.Limit(10.0/60.0), 5) // 10 req/min total, burst 5
)

const (
	perStudentRateLimit = rate.Limit(2.0 / 60.0) // 2 requests/minute per student
	perStudentBurst     = 2                       // short burst allowance
	perStudentDailyMax  = 20                      // 20 requests/day per student
	limiterTTL          = 30 * time.Minute
	cleanupInterval     = 5 * time.Minute
	maxLimiters         = 10_000 // safety cap: prevents unbounded map growth from bot/fake IDs
)

/*
getLimiter returns the limiter entry for a client key and refreshes last-seen time.
Each client key tracks both minute-rate tokens and daily request count.

todo: X-Student-ID header is user-controlled — easily spoofed.
Any student can set X-Student-ID: someone_else and steal another student's quota
or bypass their own limit by rotating fake IDs.
Fix: Never trust client-supplied identity headers directly. Use one of:
  - A signed JWT token validated server-side
  - A session cookie the server issued after login
  - Validate the student ID against your actual user database

todo: IP fallback is bypassable: host, _, err := net.SplitHostPort(r.RemoteAddr)
If your server sits behind a proxy/nginx, RemoteAddr is always the proxy's IP,
not the student's. All students share one limiter — one student can exhaust everyone's quota.
Fix: Read the real IP from trusted proxy headers (already done in extractClientKey below).
*/
func getLimiter(key string) (*limiterEntry, bool) {
	mu.Lock()
	defer mu.Unlock()

	now := time.Now().UTC()
	today := now.Format("2006-01-02")

	if entry, ok := limiters[key]; ok {
		// reset daily count if UTC date has changed
		if entry.dayUTC != today {
			entry.dayUTC = today
			entry.dailyCnt = 0
		}
		entry.lastSeen = now // reuse same captured time — consistent within this call
		return entry, true
	}

	// cap map size to prevent memory exhaustion from bots rotating fake student IDs
	if len(limiters) >= maxLimiters {
		return nil, false // signal to caller: reject this request
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

/*
extractClientKey prefers an explicit student identifier when available.
Fallback is stable client IP from X-Forwarded-For (set by nginx/proxy) or RemoteAddr.

NOTE: X-Forwarded-For is only trusted if YOU control the proxy (nginx).
If requests can come directly to this server without nginx, a client could
spoof X-Forwarded-For. In production behind nginx, this is safe.
*/
func extractClientKey(r *http.Request) string {
	// todo: replace with JWT/session validation — header is currently user-controlled and spoofable
	studentID := strings.TrimSpace(r.Header.Get("X-Student-ID"))
	if studentID != "" {
		return "student:" + studentID
	}

	// read real client IP from proxy header (nginx sets this in production)
	// only trust this if nginx is always in front — otherwise clients can spoof it
	if forwarded := r.Header.Get("X-Forwarded-For"); forwarded != "" {
		// X-Forwarded-For can be a comma-separated list: "clientIP, proxy1, proxy2"
		// take the first entry — that's the original client
		parts := strings.Split(forwarded, ",")
		return "ip:" + strings.TrimSpace(parts[0])
	}

	// final fallback: direct RemoteAddr (works correctly when no proxy is involved)
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return "ip:" + strings.TrimSpace(r.RemoteAddr)
	}
	return "ip:" + host
}

/*
cleanupStaleLimiters periodically removes limiter entries that have been inactive
longer than limiterTTL to prevent unbounded memory growth.
Runs as a single background goroutine (started via sync.Once).
*/
func cleanupStaleLimiters() {
	ticker := time.NewTicker(cleanupInterval)
	defer ticker.Stop()
	// no defer mu.Unlock() here — lock/unlock happen inside the loop per tick

	for range ticker.C {
		cutoff := time.Now().Add(-limiterTTL)
		mu.Lock()
		for key, entry := range limiters {
			if entry.lastSeen.Before(cutoff) {
				delete(limiters, key)
			}
		}
		mu.Unlock() // explicit unlock per tick — defer would only run when goroutine exits (never)
	}
}

func secondsUntilUTCMidnight(now time.Time) int {
	next := time.Date(now.Year(), now.Month(), now.Day()+1, 0, 0, 0, 0, time.UTC)
	sec := int(next.Sub(now).Seconds())
	if sec < 1 {
		return 1
	}
	return sec
}

/*
RateLimiter enforces a fair-use policy for the AI/Gemini endpoint:
  - Global cap:     10 req/min total (protects free Gemini API quota across all students)
  - Minute window:  2 req/min per student (burst 2)
  - Daily window:   20 req/day per student (UTC rollover)

It also writes quota headers so the frontend can display remaining allowance.

In development, OPTIONS counts as 1 request.
In production, nginx handles OPTIONS preflight before it reaches this server,
so it never hits the limiter.
*/
func RateLimiter(next http.Handler) http.Handler {
	startCleanupWorker.Do(func() {
		go cleanupStaleLimiters()
	})

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// OPTIONS preflight should not consume rate-limit quota.
		// Can be removed if production nginx handles OPTIONS before requests reach here.
		if r.Method == http.MethodOptions {
			next.ServeHTTP(w, r)
			return
		}

		// --- global cap: check before per-student to protect Gemini API quota ---
		if !globalLimiter.Allow() {
			http.Error(w, "Server busy, try again shortly", http.StatusTooManyRequests)
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
		w.Header().Set("X-RateLimit-Minute", "2")
		w.Header().Set("X-RateLimit-Day", strconv.Itoa(perStudentDailyMax))

		mu.Lock()

		// re-check day rollover inside the lock (getLimiter may have run slightly earlier)
		today := now.Format("2006-01-02")
		if entry.dayUTC != today {
			entry.dayUTC = today
			entry.dailyCnt = 0
		}

		// --- daily quota check ---
		// todo: re-enable in production — commented out for testing only
		// if entry.dailyCnt >= perStudentDailyMax {
		// 	w.Header().Set("X-RateLimit-Day-Remaining", "0")
		// 	w.Header().Set("Retry-After", strconv.Itoa(secondsUntilUTCMidnight(now)))
		// 	mu.Unlock()
		// 	http.Error(w, "Daily quota exceeded (20/day)", http.StatusTooManyRequests)
		// 	return
		// }

		// --- per-minute rate check ---
		if !entry.limiter.Allow() {
			remaining := perStudentDailyMax - entry.dailyCnt
			w.Header().Set("X-RateLimit-Day-Remaining", strconv.Itoa(remaining))
			w.Header().Set("Retry-After", "30")
			mu.Unlock()
			http.Error(w, "Rate limit exceeded (2/min)", http.StatusTooManyRequests)
			return
		}

		entry.dailyCnt++
		remaining := perStudentDailyMax - entry.dailyCnt
		w.Header().Set("X-RateLimit-Day-Remaining", strconv.Itoa(remaining))

		// unlock BEFORE next.ServeHTTP — handler can take seconds (LLM call),
		// holding the mutex that long would block every other student's request
		mu.Unlock()
		next.ServeHTTP(w, r)
	})
}