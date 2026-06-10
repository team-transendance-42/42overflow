package middleware

import (
	"net/http"
	"os"
)

// InternalSecret rejects any non-healthz request that doesn't carry the correct
// X-Internal-Secret header. This proves the request came from SvelteKit, not from
// someone probing the Docker-internal network directly.
func InternalSecret(next http.Handler) http.Handler {
	secret := os.Getenv("LLM_INTERNAL_SECRET")
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/healthz" {
			next.ServeHTTP(w, r)
			return
		}
		if secret == "" || r.Header.Get("X-Internal-Secret") != secret {
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}
		next.ServeHTTP(w, r)
	})
}
