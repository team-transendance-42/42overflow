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

type OllamaRequest struct {
	Model    string      `json:"model"`
	Messages []ollamaMsg `json:"messages"`
	Stream   bool        `json:"stream"`
}

type ollamaMsg struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type OllamaResponse struct {
	Message ollamaMsg `json:"message"`
	Done    bool      `json:"done"`
}

const ollamaSystemPrompt = "reply with less words, dont repeat info"

func buildOllamaMessages(msgs []models.Message) []ollamaMsg {
	out := make([]ollamaMsg, 0, len(msgs)+1)
	out = append(out, ollamaMsg{Role: "system", Content: ollamaSystemPrompt})
	for _, m := range msgs {
		out = append(out, ollamaMsg{
			Role:    string(m.Role),
			Content: m.Content,
		})
	}
	return out
}

func buildOllamaMessagesFromRequest(req models.TextRequest) []ollamaMsg {
	msgs := make([]models.Message, 0, len(req.Messages)+1)
	msgs = append(msgs, req.Messages...)

	if strings.TrimSpace(req.Prompt) != "" {
		msgs = append(msgs, models.Message{
			Role:    "user",
			Content: req.Prompt,
		})
	}

	return buildOllamaMessages(msgs)
}

func doOllamaRequest(ctx context.Context, ollamaURL, model string, req models.TextRequest) (*http.Response, error) {
	body, err := json.Marshal(OllamaRequest{
		Model:    model,
		Messages: buildOllamaMessagesFromRequest(req),
		Stream:   true,
	})
	if err != nil {
		return nil, fmt.Errorf("marshal Ollama request: %w", err)
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

func readOllamaToChannel(resp *http.Response, ch chan string) {
	defer close(ch)
	defer resp.Body.Close()
	sender := &chunkSender{}
	decoder := json.NewDecoder(resp.Body)
	for {
		var r OllamaResponse
		if err := decoder.Decode(&r); err != nil {
			if err != io.EOF {
				log.Printf("Ollama decode error: %v", err)
			}
			break
		}
		sender.send(ch, r.Message.Content)
		if r.Done {
			break
		}
	}
}

func StreamOllama(ctx context.Context, req models.TextRequest) (<-chan string, error) {
	model := os.Getenv("OLLAMA_MODEL")
	if model == "" {
		model = "gemma3"
	}
	ollamaURL := os.Getenv("OLLAMA_URL")
	if ollamaURL == "" {
		ollamaURL = "http://localhost:11434"
	}

	resp, err := doOllamaRequest(ctx, ollamaURL, model, req)
	if err != nil {
		return nil, err
	}

	ch := make(chan string)
	go readOllamaToChannel(resp, ch)
	return ch, nil
}
