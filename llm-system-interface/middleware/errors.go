package middleware

import (
	"net/http"
	"log"
)

// ErrorRecovery is a middleware that recovers from panics and returns a 500 Internal Server Error.
func ErrorRecovery(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("Recovered from panic: %v", err)
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}	
