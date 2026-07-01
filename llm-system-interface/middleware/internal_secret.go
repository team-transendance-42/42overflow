package middleware

import (
	"crypto/subtle"
	"log"
	"net/http"
	"os"
)

// InternalSecret rejects any non-healthz request that doesn't carry the correct
// X-Internal-Secret header. This proves the request came from SvelteKit, not from
// someone probing the Docker-internal network directly.
func InternalSecret(next http.Handler) http.Handler {
	secret := os.Getenv("LLM_INTERNAL_SECRET")
	if secret == "" {
		log.Fatal("LLM_INTERNAL_SECRET env var is not set — refusing to start without a valid secret")
	}
	secretBytes := []byte(secret)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/healthz" {
			next.ServeHTTP(w, r)
			return
		}
		if subtle.ConstantTimeCompare([]byte(r.Header.Get("X-Internal-Secret")), secretBytes) != 1 {
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}
		next.ServeHTTP(w, r)
	})
}
