package models

const RoleUser = "user"

// StreamErrSentinel(marker) is a prefix sent on a chan string to signal a mid-stream error.
// \x00 (null byte in ASCII) never appears in LLM text output, so it cannot be confused with real content.
const StreamErrSentinel = "\x00err:"

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

/*both gemini and ollama services accept TextRequest */
type TextRequest struct {
	Prompt   string    `json:"prompt"`             // current message (backward compatible)
	Messages []Message `json:"messages,omitempty"` // full history (optional)
}
