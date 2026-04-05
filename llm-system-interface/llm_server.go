package main

// go run llm_server.go
//https://github.com/team-transendance-42/42overflow
// /api/ai-assist route accepts a POST request with JSON like {"prompt": "your text"}, parse it, and return the prompt as the response. Under the hood, Go’s net/http decodes the JSON body into a struct.
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
	err := godotenv.Load() // Load the .env file
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	apiKey := os.Getenv("GEMINI_API_KEY") // todo: rmv, this is for testing
	if apiKey == "" {
		log.Fatal("GEMINI_API_KEY not found in environment after loading .env")
	}
	log.Println("Successfully loaded API Key.")

	router := mux.NewRouter()

	router.Use(middleware.ErrorRecovery)
	router.Use(middleware.RateLimiter)

	router.HandleFunc("/api/ai-assist", handlers.GenerateText).Methods("POST", "OPTIONS")
	router.HandleFunc("/api/generate-image", handlers.GenerateImage).Methods("POST", "OPTIONS") // placeholder for future image generation endpoint: todo: implement handlers.GenerateImage

	log.Println("Server running on port 8081")
	log.Fatal(http.ListenAndServe(":8081", router))
}
