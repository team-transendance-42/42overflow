package models

type TextRequest struct {
	Prompt string `json:"prompt"`
	Model  string `json:"model,omitempty"`  // optional backend-side override if you need it later
	Stream bool   `json:"stream,omitempty"` // kept for compatibility with older callers
}

type ImageRequest struct {
	Prompt string `json:"prompt"`
	Size   string `json:"size,omitempty"` // Optional: specify image size (e.g., "256x256", "512x512")
}
