package models

type TextRequest struct {
	Prompt string `json:"prompt"`
	Model  string `json:"model,omitempty"` // Optional: specify model if needed (e.g., "claude-2", "gpt-4")
	Stream bool   `json:"stream,omitempty"` // Optional: whether to use streaming responses?? is it?
}

type ImageRequest struct {
	Prompt string `json:"prompt"`
	Size  string `json:"size,omitempty"` // Optional: specify image size (e.g., "256x256", "512x512")
}