package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"llm-system-interface/models"
	"llm-system-interface/services"
)

func GenerateText(w http.ResponseWriter, r *http.Request) {
	var req models.TextRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	// set SSE headers for streaming response
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	flusher, ok := w.(http.Flusher) // provides the Flush() method, which forces any buffered data to be sent to the client immediately (important for streaming responses).
	if !ok {
		http.Error(w, "Streaming not supported", http.StatusInternalServerError)
		return
	}

	// stream tokens from the LLM service
	ch, err := services.StreamLLM(r.Context(), req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}

	for chunk := range ch {
		fmt.Fprintf(w, "data: %s\n\n", chunk) // SSE format: "data: <message>\n\n"
		flusher.Flush() // flush the response to the client immediately
	}

}

/**Images don't stream — they return a JSON response with a URL or base64 bytes.*/
func GenerateImage(w http.ResponseWriter, r *http.Request) {
	var req ImageRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	imageURL, err := services.GenerateImage(r.Context(), req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"url": imageURL})
}