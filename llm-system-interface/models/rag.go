package models
// TODO: not yet implemented
type RagIndexRequest struct {
	Collection string   `json:"collection,omitempty"`
	Documents  []string `json:"documents"`
}

type RagAskRequest struct {
	Collection string `json:"collection,omitempty"`
	Question   string `json:"question"`
	TopK       int    `json:"top_k,omitempty"`
}

type RagAskResponse struct {
	Answer   string   `json:"answer"`
	Contexts []string `json:"contexts"`
}

// RagRetrieveContext is one context hit from the Python /rag/retrieve endpoint.
type RagRetrieveContext struct {
	ID       string  `json:"id"`
	Text     string  `json:"text"`
	RRFScore float64 `json:"rrf_score"`
}

// RagRetrieveResponse is the JSON response from Python /rag/retrieve.
type RagRetrieveResponse struct {
	Contexts   []RagRetrieveContext `json:"contexts"`
	Confidence float64              `json:"confidence"`
}
