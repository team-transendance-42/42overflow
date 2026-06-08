// handlers/ollama_handler.go
package handlers

import (
	"llm-system-interface/models"
	"llm-system-interface/services"
	"log"
	"net/http"
	"time"
)

// This is the "Line". A capacity of 1 means only 1 student at a time.
var ollamaQueue = make(chan struct{}, 1)

/**
implememts a buffered channel as a semaphore to manage concurrent access to a local LLM. Since the environment is CPU-bound(my laptop), this prevents resource exhaustion and ensured system stability under multi-user load; otherwise: Possible server crashes or instability if the system runs out of CPU or memory.
*/
func GenerateOllamaText(w http.ResponseWriter, r *http.Request) {
	log.Printf("GenerateOllamaText(): method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) {
		return
	}
	// 1. GET IN LINE
	// ollamaQueue <- struct{}{}
	select {
	case ollamaQueue <- struct{}{}:
	case <-r.Context().Done():
		return
	case <-time.After(30 * time.Second):
		http.Error(w, "Ollama is busy, try again shortly", http.StatusServiceUnavailable)
		return
	}
	defer func() { 
        <-ollamaQueue 
        log.Println("Ollama slot released for next student.")
    }()

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