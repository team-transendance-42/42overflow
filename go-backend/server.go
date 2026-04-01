package main
//go run ./
// http://localhost:8081/api/ask
import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

/**
The OPTIONS method is an HTTP request used by browsers to ask the server which HTTP methods and headers are allowed for a specific resource. It’s mostly used for CORS (Cross-Origin Resource Sharing) preflight requests.

Prompt is a field name
*/
func askHandler(w http.ResponseWriter, r *http.Request) {
	 // CORS(cross-origin resource sharing) headers for api endpoint
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

	apiKey := os.Getenv("ANTHROPIC_API_KEY")
	if apiKey == "" {
		http.Error(w, "API key not set", http.StatusInternalServerError)
		return
	}
	client := NewLLMClient(apiKey)
	answer, err := client.Generate(req.Prompt)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"response": answer})
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081" // swelte runs on 5173
	}
	http.HandleFunc("/api/ask", askHandler)
	fmt.Println("Go API server running on http://localhost:" + port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
