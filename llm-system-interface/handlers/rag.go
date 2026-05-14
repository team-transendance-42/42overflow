package handlers

import (
	"encoding/json"
	"fmt"
	"llm-system-interface/models"
	"llm-system-interface/services"
	"log"
	"net/http"
	"strings"
)

// RagAskStreaming handles POST /api/community.
// Retrieves community contexts from the Python RAG service and streams
// Gemma's answer constrained to those contexts.
func RagAskStreaming(w http.ResponseWriter, r *http.Request) {
	log.Printf("RagAskStreaming(): method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) {
		return
	}

	// Share the Ollama semaphore — one Ollama request at a time
	ollamaQueue <- struct{}{}
	defer func() {
		<-ollamaQueue
		log.Println("Ollama slot released after Community request.")
	}()

	var req models.TextRequest
	if !decodeAndSanitize(w, r, &req) {
		return
	}
	if strings.TrimSpace(req.Prompt) == "" {
		http.Error(w, "prompt is required", http.StatusBadRequest)
		return
	}

	ch, contexts, confidence, err := services.StreamRagAnswer(r.Context(), req.Prompt)
	if err != nil {
		log.Printf("RagAskStreaming: StreamRagAnswer error: %v", err)
		http.Error(w, "Community service error: "+err.Error(), http.StatusBadGateway)
		return
	}

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming not supported", http.StatusInternalServerError)
		return
	}

	metaJSON, _ := json.Marshal(map[string]any{
		"contexts":   contexts,
		"confidence": confidence,
	})
	fmt.Fprintf(w, "event: meta\ndata: %s\n\n", metaJSON)
	flusher.Flush()

	streamSSE(w, ch)
}
