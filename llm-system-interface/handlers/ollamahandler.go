package handlers

import (
	"fmt"
	"llm-system-interface/models"
	"llm-system-interface/services"
	"log"
	"net/http"
	"strings"
)

// GenerateOllamaText streams Ollama responses using Server-Sent Events
func GenerateOllamaText(w http.ResponseWriter, r *http.Request) {
	log.Printf("GenerateOllamaText(): method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) {
		return
	}

	var req models.TextRequest
	if !validateTextReq(w, r, &req) {
		return
	}

	ch, err := services.StreamOllama(r.Context(), req.Prompt)
	if err != nil {
		log.Printf("GenerateOllamaText: StreamOllama error: %v", err)
		http.Error(w, "Ollama Service Error: "+err.Error(), http.StatusBadGateway)
		return
	}

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming not supported", http.StatusInternalServerError)
		return
	}

	for chunk := range ch {
		for _, line := range strings.Split(chunk, "\n") {
			fmt.Fprintf(w, "data: %s\n", line)
		}
		fmt.Fprint(w, "\n")
		flusher.Flush()
	}

	fmt.Fprintf(w, "event: end\ndata: \n\n")
	flusher.Flush()
}