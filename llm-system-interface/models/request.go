package models

type Role string

const (
	RoleUser      Role = "user"
	RoleAssistant Role = "assistant"
	RoleSystem    Role = "system"
)

type Message struct {
	Role    Role   `json:"role"`
	Content string `json:"content"`
}

type TextRequest struct {
	Prompt   string    `json:"prompt"`             // current message (backward compatible)
	Messages []Message `json:"messages,omitempty"` // full history (optional)
	Model    string    `json:"model,omitempty"`
	Stream   bool      `json:"stream,omitempty"`
}

type ImageRequest struct {
	Prompt string `json:"prompt"`
	Size   string `json:"size,omitempty"`
}
