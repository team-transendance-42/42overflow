package middleware

import (
	"net/http"
	"sync"
	"golang.org/x/time/rate"
)

var (
	limiters = make(map[string]*rate.Limiter)
	mu       sync.Mutex
)

/**
*rate.Limiter is a pointer to a Limiter struct from the rate package in golang.org/x/time/rate. This package is not built-in to Go’s standard library, but is an official Go extension package.
Limiter is a type (struct) in that package, used for rate limiting (controlling how frequently actions can happen).
*rate.Limiter means a pointer to a Limiter.
You need to import "golang.org/x/time/rate" to use it. It’s commonly used for implementing rate limiting in Go web servers.
*/
func getLimiter(ip string) *rate.Limiter {
	mu.Lock()
	defer mu.Unlock()
	if l, ok := limiters[ip]; ok {
		return l
	}
	l := rate.NewLimiter(rate.Limit(10), 20) // 10 tokens per second, burst of 20
	limiters[ip] = l
	return l
}

// https://pkg.go.dev/net/http#Handler
// TODO!! For production, add an expiry map to clean up old IPs — otherwise memory leaks. Use time.AfterFunc or a background goroutine with a ticker.
func RateLimiter(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		limiter := getLimiter(r.RemoteAddr)
		if !limiter.Allow() {
			http.Error(w, "Too Many Requests", http.StatusTooManyRequests) // 429 status code
			return
		}
		next.ServeHTTP(w, r)
	})
}