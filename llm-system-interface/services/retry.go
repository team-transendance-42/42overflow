package services

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"
)

const (
	maxRetries = 3
	baseDelay  = time.Second // 1s=1,000,000,000 nanoseconds
)

// returns true for transient errors worth retrying.
func retryableStatus(code int) bool {
	return code == http.StatusTooManyRequests ||
		code == http.StatusServiceUnavailable ||
		code == http.StatusGatewayTimeout
}

/*
Safely disposes of an HTTP response body — reads and discards remaining bytes, then closes it
reads up to 4KB from body so the TCP connection can be
returned to the pool, then closes it. The cap prevents blocking on a
misbehaving server that streams a huge error page.
*/
func drainAndClose(body io.ReadCloser) {
	io.Copy(io.Discard, io.LimitReader(body, 4096))
	body.Close()
}

/*
  io.ReadCloser is an interface — any type that has both Read([]byte) (int, error) and Close() error methods satisfies it. HTTP response bodies implement this.
*/
/* withRetry calls fn up to maxRetries times with exponential backoff.
It retries only on network errors or retryable HTTP status codes.
The returned response is open — caller must close it on success.
handles 429 (rate limited), 503 (service unavailable), and 504 (gateway timeout) — these are all transient, the right response is wait and retry.
*/
func withRetry(ctx context.Context, fn func() (*http.Response, error)) (*http.Response, error) {
	delay := baseDelay
	var lastErr error
	for i := range maxRetries {
		if i > 0 {
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(delay):
				delay *= 2
			}
		}
		resp, err := fn()
		if err != nil {
			lastErr = err
			log.Printf("retry %d/%d: request error: %v", i+1, maxRetries, err)
			continue
		}
		if !retryableStatus(resp.StatusCode) {
			return resp, nil
		}
		lastErr = fmt.Errorf("HTTP %d", resp.StatusCode)
		drainAndClose(resp.Body)
		log.Printf("retry %d/%d: HTTP %d", i+1, maxRetries, resp.StatusCode)
	}
	return nil, fmt.Errorf("max retries exceeded: %w", lastErr)
}
