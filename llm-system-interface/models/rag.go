package models

// RagRetrieveContext is one context hit from the Python /rag/retrieve endpoint.
type RagRetrieveContext struct {
	ID       string  `json:"id"`
	Text     string  `json:"text"`
	RRFScore float64 `json:"rrf_score"`
}

// RagRetrieveResponse is the JSON response from Python /rag/retrieve.
type RagRetrieveResponse struct {
	Contexts       []RagRetrieveContext `json:"contexts"`
	Confidence     float64              `json:"confidence"`
	BestSimilarity float64              `json:"best_similarity"`
}
