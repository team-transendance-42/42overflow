package main

// go run llm_server.go
//https://github.com/team-transendance-42/42overflow
/* /api/ai-assist route accepts a POST req with JSON like {"prompt": "text"}, parse it, and return the prompt as the response. Under the hood, Go’s net/http decodes the JSON body into a struct.
*/
//curl -X POST -H "Content-Type: application/json" -d '{"prompt":"hello world"}' http://localhost:8081/api/ai-assist
import (
	"llm-system-interface/handlers"
	"llm-system-interface/middleware"
	"log"
	"net/http"
	"os"
	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Println("No .env file loaded, using container/runtime environment variables")
	}
	if os.Getenv("GEMINI_API_KEY") == "" {
		log.Fatal("GEMINI_API_KEY is required")
	}
	log.Println("Successfully loaded API Key.")

	router := mux.NewRouter() // contains list of routes, middleware chain, config flags(strict slash, etc)
	router.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	}).Methods(http.MethodGet)

	middleware.StartCleanup() // background go routine with infinate loop, sleeps 5 min, cleans
	router.Use(middleware.ErrorRecovery) //ErrorRecovery lets execution flow to RateLimiter only if no panic occurs.
	router.Use(middleware.RateLimiter)

	router.HandleFunc("/api/ai-assist", handlers.GenerateText).Methods("POST", "OPTIONS")
	router.HandleFunc("/api/ollama", handlers.GenerateOllamaText).Methods("POST", "OPTIONS")
	// router.HandleFunc("/api/rag/index", handlers.RagIndex).Methods("POST", "OPTIONS") todo: implement RAG indexing endpoint, which accepts text and metadata, and stores it in a vector database like Pinecone or Weaviate. This is separate from the /ask endpoint, which only retrieves info.
	// router.HandleFunc("/api/rag/ask", handlers.RagAsk).Methods("POST", "OPTIONS")
	//router.HandleFunc("/api/generate-image", handlers.GenerateImage).Methods("POST", "OPTIONS") // placeholder for future image generation endpoint: todo: implement handlers.GenerateImage

	log.Println("Server running on port 8081")
	log.Fatal(http.ListenAndServe(":8081", router))
}
