package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

// Handler for /api/ask
func askHandler(w http.ResponseWriter, r *http.Request) {
	 // CORS headers for development
    w.Header().Set("Access-Control-Allow-Origin", "*")
    w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
    w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

    if r.Method == "OPTIONS" {
        w.WriteHeader(http.StatusOK)
        return
    }
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Prompt string `json:"prompt"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	// Call your LLM logic here (replace this with your real function)
	response := "Echo: " + req.Prompt

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"response": response})
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081" // swelte runs on 8080
	}
	http.HandleFunc("/api/ask", askHandler)
	fmt.Println("Go API server running on http://localhost:" + port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
