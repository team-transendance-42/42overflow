package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"llm-system-interface/models"
	"log"
	"net/http"
	"os"
	"strings"
)
/*
Ollama
======================================
messages:   	{role, content}
system prompt: 	role:system
role name:     "assistant"
extra fields: stream

=====================================
Gemini
=====================================
messages:     	{role, parts:[{text}]}
system prompt:  system_instruction, top-level field
role name:      "model"
extra fields:   system_instruction, multimodal parts
*/
type OllamaRequest struct {
	Model    string           `json:"model"`
	Messages []models.Message `json:"messages"`
	Stream   bool             `json:"stream"`
}

type OllamaResponse struct {
	Message models.Message `json:"message"`
	Done    bool           `json:"done"`
}

func truncate(s string, n int) string {
	if (len(s) > n) {
		return s[:n]
	}
	return s
}

/**
In Go, the maximum length of a string you can send through a channel (like ch <- r.Message.Content) is limited by available memory, not by the channel itself. The channel transmits the string as a value, and Go strings can be up to 2GB (on 32-bit systems) or much larger (on 64-bit systems), but in practice, you are limited by system memory and performance.
*/
func buildOllamaMessages(req models.TextRequest) []models.Message {
    const systemPrompt = "reply with less words, dont repeat info"
    const maxHistory = 10
	const maxContentLen = 2000 // chars per msg

    msgs := make([]models.Message, 0, len(req.Messages)+1)
    for _, m := range req.Messages {
        msgs = append(msgs, models.Message{Role: m.Role, Content: truncate(m.Content, maxContentLen)})
    }
    if strings.TrimSpace(req.Prompt) != "" {
        msgs = append(msgs, models.Message{Role: "user", Content: truncate(req.Prompt, maxContentLen)})
    }
    if len(msgs) > maxHistory {
        msgs = msgs[len(msgs)-maxHistory:]
    }
    return append([]models.Message{{Role: "system", Content: systemPrompt}}, msgs...)
}

/*
ollamaURL+"/api/chat": Ollama always exposes /api/chat — it's their fixed endpoint
*/
func doOllamaRequest(ctx context.Context, ollamaURL, model string, req models.TextRequest) (*http.Response, error) {
	body, err := json.Marshal(OllamaRequest{ //serializes the OllamaRequest struct into a JSON byte slice
		Model:    model,
		Messages: buildOllamaMessages(req),
		Stream:   true,
	})
	if err != nil {
		return nil, fmt.Errorf("marshal Ollama request: %w", err) //%w = wrap verb for errors
	}

	return withRetry(ctx, func() (*http.Response, error) {
		reqHTTP, err := http.NewRequestWithContext(ctx, "POST", ollamaURL+"/api/chat", bytes.NewReader(body))
		if err != nil {
			return nil, fmt.Errorf("build Ollama request: %w", err)
		}
		reqHTTP.Header.Set("Content-Type", "application/json")
		return http.DefaultClient.Do(reqHTTP)
	})
}

/*
defer: no matter what happens (early return, error, normal exit) the body always gets closed and no resources are leaked
*/
func readOllamaToChannel(ctx context.Context, resp *http.Response, ch chan string) {
	defer close(ch)
	defer resp.Body.Close()
	decoder := json.NewDecoder(resp.Body)
	for {
		var r OllamaResponse
		if err := decoder.Decode(&r); err != nil {
			if err != io.EOF && ctx.Err() == nil {
				log.Printf("Ollama decode error: %v", err)
			}
			break
		}
		if r.Message.Content != "" {
			ch <- r.Message.Content
		}
		if r.Done {
			break
		}
	}
}

func StreamOllama(ctx context.Context, req models.TextRequest) (<-chan string, error) {
	model := os.Getenv("OLLAMA_MODEL")
	ollamaURL := os.Getenv("OLLAMA_URL")
	if model == "" || ollamaURL == "" {
		return nil, fmt.Errorf("OLLAMA_URL and OLLAMA_MODEL must be set")
	}

	resp, err := doOllamaRequest(ctx, ollamaURL, model, req)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("ollama HTTP %d: %s", resp.StatusCode, strings.TrimSpace(string(body)))
	}

	ch := make(chan string)
	go readOllamaToChannel(ctx, resp, ch)
	return ch, nil
}
