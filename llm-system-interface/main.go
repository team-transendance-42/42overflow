package main

// go run main.go
// in browser: http://locahost:8080/generate
//https://github.com/team-transendance-42/42overflow
// step 2: You want your /generate route to accept a POST request with JSON like {"prompt": "your text"}, parse it, and return the prompt as the response. Under the hood, Go’s net/http decodes the JSON body into a struct.
//curl -X POST -H "Content-Type: application/json" -d '{"prompt":"hello world"}' http://localhost:8080/generate
import (
	"log"
	"net/http"
	"github.com/gorilla/mux"
	"encoding/json"
	"llm-system-interface/models"
)

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/generate", func(w http.ResponseWriter, r *http.Request) {
		var req models.TextRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}
		w.Write([]byte(req.Prompt))
	}).Methods("POST")

	log.Println("Server running on port 8080")
	log.Fatal(http.ListenAndServe(":8080", r))
}