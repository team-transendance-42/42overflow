package handlers

import (
	"llm-system-interface/models"
	"llm-system-interface/services"
	"log"
	"net/http"
	"strings"
	"time"
)

// ragQueue is a separate semaphore for RAG requests.
// Capacity 1: only one community request runs at a time (Ollama is CPU-bound).
// Kept separate from ollamaQueue so a slow RAG request does not block plain Ollama requests.
var ragQueue = make(chan struct{}, 1)

// RagAskStreaming handles POST /ai-assist/community.
// Retrieves community contexts from the Python RAG service and streams
// Gemma's answer constrained to those contexts.
func RagAskStreaming(w http.ResponseWriter, r *http.Request) {
	log.Printf("RagAskStreaming(): method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) {
		return
	}

	select {
	case ragQueue <- struct{}{}:
	case <-r.Context().Done():
		return
	case <-time.After(30 * time.Second):
		http.Error(w, "Community service busy, try again shortly", http.StatusServiceUnavailable)
		return
	}
	defer func() {
		<-ragQueue
		log.Println("RAG slot released after Community request.")
	}()

	var req models.TextRequest
	if !decodeAndSanitize(w, r, &req) {
		return
	}
	if strings.TrimSpace(req.Prompt) == "" {
		http.Error(w, "prompt is required", http.StatusBadRequest)
		return
	}
	if len(req.Prompt) > 20000 {
		http.Error(w, "prompt too large, max 20000 chars", http.StatusRequestEntityTooLarge)
		return
	}

	ch, err := services.StreamRagAnswer(r.Context(), req.Prompt)
	if err != nil {
		log.Printf("RagAskStreaming: StreamRagAnswer error: %v", err)
		http.Error(w, "Community service error: "+err.Error(), http.StatusBadGateway)
		return
	}

	streamSSE(w, ch)
}
