package models

const RoleUser      = "user"

type Message struct {
	Role    string   `json:"role"`
	Content string `json:"content"`
}

/*both gemini and ollama services accept TextRequest */
type TextRequest struct {
	Prompt   string    `json:"prompt"`             // current message (backward compatible)
	Messages []Message `json:"messages,omitempty"` // full history (optional)
	Model    string    `json:"model,omitempty"`
	Stream   bool      `json:"stream,omitempty"`
}
