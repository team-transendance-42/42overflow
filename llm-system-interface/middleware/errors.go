package middleware

import (
	"net/http"
	"log"
)

// ErrorRecovery is a middleware that recovers from panics and returns a 500 Internal Server Error.
/**
The defer keyword pushes a function call onto a stack. This function is guaranteed to execute after the surrounding function returns, regardless of whether it finished successfully or crashed. This is the only place in Go where you can safely catch a panic. Since a panic unwinds the stack, the defer block is the final "catch-all" before the goroutine terminates.
*/
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
