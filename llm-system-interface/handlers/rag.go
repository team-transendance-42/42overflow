package handlers

import (
	"encoding/json"
	"llm-system-interface/models"
	"llm-system-interface/services"
	"net/http"
	"strings"
)

func RagIndex(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusNoContent)
		return
	}
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req models.RagIndexRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	if len(req.Documents) == 0 {
		http.Error(w, "documents are required", http.StatusBadRequest)
		return
	}

	count, err := services.IndexDocuments(r.Context(), req.Collection, req.Documents)
	if err != nil {
		http.Error(w, "RAG index error: "+err.Error(), http.StatusBadGateway)
		return
	}
	collection := strings.TrimSpace(req.Collection)
	if collection == "" {
		collection = "my_rag_collection"
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]any{
		"ok":         true,
		"indexed":    count,
		"collection": collection,
	})
}

func RagAsk(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusNoContent)
		return
	}
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req models.RagAskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}
	if strings.TrimSpace(req.Question) == "" {
		http.Error(w, "question is required", http.StatusBadRequest)
		return
	}

	answer, contexts, err := services.AskRag(r.Context(), req.Collection, req.Question, req.TopK)
	if err != nil {
		http.Error(w, "RAG ask error: "+err.Error(), http.StatusBadGateway)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(models.RagAskResponse{
		Answer:   answer,
		Contexts: contexts,
	})
}
