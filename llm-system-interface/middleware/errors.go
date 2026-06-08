package middleware

import (
	"net/http"
	"log"
)

// ErrorRecovery is a middleware that recovers from panics and returns a 500 Internal Server Error.
/**
defer pushes a call onto a stack. When the surrounding function returns (or panics), deferred calls execute LIFO (last in, first out).
Without recover() inside a defer, a panic would crash the entire goroutine (and potentially the server). This pattern is idiomatic Go for building resilient HTTP servers.
Imagine the HTTP server is a chef in a kitchen. Sometimes the chef might accidentally drop everything and cause a disaster (a panic in Go). This function is like a safety net under the chef — if something goes wrong, it catches the mess, cleans up, and calmly tells the customer "Sorry, something went wrong" instead of the whole kitchen burning down.
*/
func ErrorRecovery(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() { //defer schedules a function to run at the very end, no matter what happens — even if the program crashes.
			if err := recover(); err != nil { // recover() only works inside a deferred function — that's the only place Go lets you intercept a panic mid-flight.
				log.Printf("Recovered from panic: %v", err)
				http.Error(w, "Internal Server Error", http.StatusInternalServerError) //Sends an HTTP 500 response back to the client.
			}
		}()
		next.ServeHTTP(w, r) //next is an interface — specifically http.Handler from the standard library net/http package. next can be anything that has ServeHTTP — a router, another middleware, a plain handler function
	})
}	
