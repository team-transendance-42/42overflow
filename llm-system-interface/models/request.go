package models

type TextRequest struct {
	Prompt string `json:"prompt"`
	Model  string `json:"model,omitempty"`  // app-level model selection, mapped in service
	Stream bool   `json:"stream,omitempty"` // app-level flag; service chooses Gemini streaming or non-streaming API
}

type ImageRequest struct {
	Prompt string `json:"prompt"`
	Size  string `json:"size,omitempty"` // Optional: specify image size (e.g., "256x256", "512x512")
}