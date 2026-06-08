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
