// services/retry.go
package services

import (
	"context"
	"log"
	"net/http"
	"time"
	"fmt"
)

const (
	maxRetries = 3
	baseDelay  = time.Second
)

// retryableStatus returns true for transient errors worth retrying.
func retryableStatus(code int) bool {
	return code == http.StatusTooManyRequests ||
		code == http.StatusServiceUnavailable ||
		code == http.StatusGatewayTimeout
}

// withRetry calls fn up to maxRetries times with exponential backoff.
// It retries only on network errors or retryable HTTP status codes.
// The returned response is open — caller must close it on success.
// handles 429 (rate limited), 503 (service unavailable), and 504 (gateway timeout) — these are all transient, the right response is wait and retry.
func withRetry(ctx context.Context, fn func() (*http.Response, error)) (*http.Response, error) {
	delay := baseDelay
	var lastErr error
	for i := range maxRetries {
		resp, err := fn()
		if err == nil && !retryableStatus(resp.StatusCode) {
			return resp, nil
		}
		if err != nil {
			lastErr = err
			log.Printf("retry %d/%d: request error: %v", i+1, maxRetries, err)
		} else {
			lastErr = nil
			resp.Body.Close()
			log.Printf("retry %d/%d: HTTP %d", i+1, maxRetries, resp.StatusCode)
		}
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-time.After(delay):
			delay *= 2
		}
	}
	if lastErr != nil {
		return nil, lastErr
	}
	return nil, fmt.Errorf("max retries exceeded")
}