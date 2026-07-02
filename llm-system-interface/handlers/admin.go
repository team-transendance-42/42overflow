package handlers

import (
	"encoding/json"
	"llm-system-interface/services"
	"log"
	"net/http"
)

// ClearRAGCacheHandler handles POST /admin/clear-rag-cache.
// Called by the Python RAG service after /admin/sync-chroma so that stale
// cached answers don't outlive a corpus update. Auth is enforced by the
// InternalSecret middleware applied to all routes.
func ClearRAGCacheHandler(w http.ResponseWriter, r *http.Request) {
	n := services.ClearRAGCache()
	log.Printf("[admin] RAG cache cleared — %d entries removed", n)
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]int{"cleared": n})
}
