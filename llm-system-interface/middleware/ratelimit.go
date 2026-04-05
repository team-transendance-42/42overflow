package middleware

import (
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	"golang.org/x/time/rate"
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
	startCleanupWorker sync.Once
)

const (
	perStudentRateLimit = rate.Limit(2.0 / 60.0) // 2 requests/minute
	perStudentBurst     = 2                      // short burst allowance
	perStudentDailyMax  = 20                     // 20 requests/day
	limiterTTL          = 30 * time.Minute
	cleanupInterval     = 5 * time.Minute
)

/*
*
getLimiter returns the limiter entry for a client key and refreshes last-seen time.
Each client key tracks both minute-rate tokens and daily request count.
*/
func getLimiter(key string) *limiterEntry {
	mu.Lock()
	defer mu.Unlock()
	now := time.Now().UTC()
	today := now.Format("2006-01-02")

	if entry, ok := limiters[key]; ok {
		if entry.dayUTC != today {
			entry.dayUTC = today
			entry.dailyCnt = 0
		}
		entry.lastSeen = time.Now()
		return entry
	}

	entry := &limiterEntry{
		limiter:  rate.NewLimiter(perStudentRateLimit, perStudentBurst),
		dayUTC:   today,
		dailyCnt: 0,
		lastSeen: time.Now(),
	}
	limiters[key] = entry
	return entry
}

/*
*
extractClientKey prefers an explicit student identifier when available.
Fallback is stable client IP from RemoteAddr (without port).
*/
func extractClientKey(r *http.Request) string {
	studentID := strings.TrimSpace(r.Header.Get("X-Student-ID"))
	if studentID != "" {
		return "student:" + studentID
	}

	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return "ip:" + strings.TrimSpace(r.RemoteAddr)
	}
	return "ip:" + host
}

/*
*
cleanupStaleLimiters periodically removes limiter entries that have been inactive
longer than limiterTTL to prevent unbounded memory growth.
*/
func cleanupStaleLimiters() {
	ticker := time.NewTicker(cleanupInterval)
	defer ticker.Stop()

	for range ticker.C {
		cutoff := time.Now().Add(-limiterTTL)
		mu.Lock()
		for key, entry := range limiters {
			if entry.lastSeen.Before(cutoff) {
				delete(limiters, key)
			}
		}
		mu.Unlock()
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
*
RateLimiter enforces a fair policy for the AI endpoint:
- Minute window: 2 requests/minute (burst 2)
- Daily window: 20 requests/day (UTC)
It also writes quota headers so the frontend can display remaining allowance.
in development, options is counted as 1 request, in production, options is free(doesnt reach our server: nginx handles it before req comes here) and doesn't hit the limiter.
*/
func RateLimiter(next http.Handler) http.Handler {
	startCleanupWorker.Do(func() {
		go cleanupStaleLimiters()
	})

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// OPTIONS preflight should not consume rate-limit quota.
		// This can be removed if production nginx handles OPTIONS and preflight
		// never reaches the Go LLM server.
		if r.Method == http.MethodOptions {
			next.ServeHTTP(w, r)
			return
		}

		entry := getLimiter(extractClientKey(r))
		now := time.Now().UTC()

		w.Header().Set("X-RateLimit-Minute", "2")
		w.Header().Set("X-RateLimit-Day", strconv.Itoa(perStudentDailyMax))

		mu.Lock()
		today := now.Format("2006-01-02")
		if entry.dayUTC != today {
			entry.dayUTC = today
			entry.dailyCnt = 0
		}

		// if entry.dailyCnt >= perStudentDailyMax {
		// 	remaining := 0
		// 	mu.Unlock()
		// 	w.Header().Set("X-RateLimit-Day-Remaining", strconv.Itoa(remaining))
		// 	w.Header().Set("Retry-After", strconv.Itoa(secondsUntilUTCMidnight(now)))
		// 	http.Error(w, "Daily quota exceeded (20/day)", http.StatusTooManyRequests)
		// 	return
		// } commented out for testing, re-enable in prod

		if !entry.limiter.Allow() {
			remaining := perStudentDailyMax - entry.dailyCnt
			mu.Unlock()
			w.Header().Set("X-RateLimit-Day-Remaining", strconv.Itoa(remaining))
			w.Header().Set("Retry-After", "30")
			http.Error(w, "Rate limit exceeded (2/min)", http.StatusTooManyRequests)
			return
		}

		entry.dailyCnt++
		remaining := perStudentDailyMax - entry.dailyCnt
		mu.Unlock()

		w.Header().Set("X-RateLimit-Day-Remaining", strconv.Itoa(remaining))
		next.ServeHTTP(w, r)
	})
}
