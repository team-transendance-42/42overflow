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
	limiter  	*rate.Limiter
	dayUTC   	string
	dailyCnt	int // tokens
	cntPerMin	int // tokens: todo
	lastSeen 	time.Time
}

var (
	mu            sync.Mutex
	limiters      = make(map[string]*limiterEntry)
	globalLimiter = rate.NewLimiter(rate.Limit(10.0/60.0), 5)
)

// todo: clean: waht we really use
const (
	perStudentRateLimit = rate.Limit(2.0 / 60.0) // 2 requests/minute per student
	perStudentBurst     = 2                       // short burst allowance
	perStudentDailyMax  = 20                      // 20 requests/day per student
	limiterTTL          = 30 * time.Minute // not used
	cleanupInterval     = 5 * time.Minute // not used
	maxLimiters         = 10_000 // safety cap: prevents unbounded map growth from bot/fake IDs -> used
)

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

func extractClientKey(r *http.Request) string {
    host, _, err := net.SplitHostPort(r.RemoteAddr)
    if err != nil {
        return "ip:" + strings.TrimSpace(r.RemoteAddr)
    }
    return "ip:" + host
}

/**
lowercase name = private to that package
uppercase name = exported
*/
func StartCleanup() {
	go func() {
		for {
			time.Sleep(cleanupInterval)

			mu.Lock()
			now := time.Now().UTC()

			for key, entry := range limiters {
				if now.Sub(entry.lastSeen) > limiterTTL {
					delete(limiters, key)
				}
			}

			mu.Unlock()
		}
	}()
}

func RateLimiter(next http.Handler) http.Handler {
	return http.HandlerFunc(func (w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodOptions {
			next.ServeHTTP(w, r)
			return
		}

		// --- global cap: check before per-student to protect Gemini API quota ---todo
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

		// --- per-minute rate check --- todo: test do we see this text?
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
		
		mu.Unlock()
		// call next handler
		next.ServeHTTP(w,r)
	})
}