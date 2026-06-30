package main

// go run llm_server.go
//https://github.com/team-transendance-42/42overflow
import (
	"llm-system-interface/handlers"
	"llm-system-interface/middleware"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Println("No .env file loaded, using container/runtime environment variables")
	}

	router := mux.NewRouter() // contains list of routes, middleware chain, config flags(strict slash, etc)
	router.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	}).Methods(http.MethodGet)

	middleware.StartCleanup()             // background go routine with infinate loop, sleeps 5 min, cleans
	router.Use(middleware.ErrorRecovery)  //ErrorRecovery lets execution flow to RateLimiter only if no panic occurs.
	router.Use(middleware.InternalSecret) // reject requests without valid X-Internal-Secret header
	router.Use(middleware.RateLimiter)

	// url: what client calls
	router.HandleFunc("/api/ai/gemini", handlers.GenerateGeminiText).Methods("POST")
	router.HandleFunc("/api/ai/ollama", handlers.GenerateOllamaText).Methods("POST")
	router.HandleFunc("/api/ai/community", handlers.RagAskStreaming).Methods("POST")

	log.Println("Server running on port 8081")
	log.Fatal(http.ListenAndServe(":8081", router))
}
