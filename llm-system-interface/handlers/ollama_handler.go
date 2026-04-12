// handlers/ollama_handler.go
package handlers

import (
	"llm-system-interface/models"
	"llm-system-interface/services"
	"log"
	"net/http"
)

func GenerateOllamaText(w http.ResponseWriter, r *http.Request) {
	log.Printf("GenerateOllamaText(): method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) {
		return
	}

	var req models.TextRequest
	if !validateTextReq(w, r, &req) {
		return
	}

	ch, err := services.StreamOllama(r.Context(), req)
	if err != nil {
		log.Printf("GenerateOllamaText: StreamOllama error: %v", err)
		http.Error(w, "Ollama Service Error: "+err.Error(), http.StatusBadGateway)
		return
	}

	streamSSE(w, ch)
}