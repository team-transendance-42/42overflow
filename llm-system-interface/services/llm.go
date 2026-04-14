// services/llm.go
package services

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"llm-system-interface/models"
	"log"
	"net/http"
	"os"
	"strings"
)

func extractTextFromJSON(data string, text *string) bool {
	var chunk struct {
		Candidates []struct {
			Content struct {
				Parts []struct {
					Text string `json:"text"`
				} `json:"parts"`
			} `json:"content"`
		} `json:"candidates"`
	}

	if err := json.Unmarshal([]byte(data), &chunk); err != nil {
		log.Printf("extractTextFromJSON() failed: %v, data=%q", err, data)
		return false
	}
	if len(chunk.Candidates) == 0 || len(chunk.Candidates[0].Content.Parts) == 0 {
		log.Println("extractTextFromJSON(): no candidates or parts in chunk")
		return false
	}
	*text = chunk.Candidates[0].Content.Parts[0].Text
	if strings.TrimSpace(*text) == "" {
		log.Println("extractTextFromJSON(): empty text chunk")
		return false
	}
	return true
}

func readGeminiSSEToChannel(resp *http.Response, ch chan string) {
	defer close(ch)
	defer resp.Body.Close()
	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		line := scanner.Text()
		if !strings.HasPrefix(line, "data: ") {
			continue
		}
		text := ""
		if !extractTextFromJSON(strings.TrimPrefix(line, "data: "), &text) {
			continue
		}
		ch <- text
	}
}

func doGEMINIRequest(ctx context.Context, client *http.Client, body []byte, apiKey string) (*http.Response, error) {
	url := os.Getenv("GEMINI_URL")
	model := os.Getenv("GEMINI_MODEL")
	if model == "" {
		model = "gemini-2.0-flash"
	}
	if url == "" {
		url = fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/%s:streamGenerateContent?alt=sse", model)
	}

	return withRetry(ctx, func() (*http.Response, error) {
		httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
		if err != nil {
			return nil, fmt.Errorf("build Gemini request: %w", err)
		}
		httpReq.Header.Set("Content-Type", "application/json")
		httpReq.Header.Set("x-goog-api-key", apiKey)
		return client.Do(httpReq)
	})
}

func buildGeminiContents(msgs []models.Message) []map[string]any {
	contents := make([]map[string]any, 0, len(msgs))
	for _, m := range msgs {
		role := string(m.Role)
		if role == "assistant" {
			role = "model"
		}
		contents = append(contents, map[string]any{
			"role": role,
			"parts": []map[string]string{
				{"text": m.Content},
			},
		})
	}
	return contents
}

func buildGeminiContentsFromRequest(req models.TextRequest) []map[string]any {
	msgs := make([]models.Message, 0, len(req.Messages)+1)
	msgs = append(msgs, req.Messages...)

	if strings.TrimSpace(req.Prompt) != "" {
		msgs = append(msgs, models.Message{
			Role:    "user",
			Content: req.Prompt,
		})
	}

	return buildGeminiContents(msgs)
}

const geminiSystemPrompt = "reply with less words, dont repeat info"

func StreamLLM(ctx context.Context, req models.TextRequest) (<-chan string, error) {
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		return nil, fmt.Errorf("GEMINI_API_KEY is not set in environment")
	}

	body, err := json.Marshal(map[string]any{
		"system_instruction": map[string]any{
			"parts": []map[string]string{
				{"text": geminiSystemPrompt},
			},
		},
		"contents": buildGeminiContentsFromRequest(req),
	})
	if err != nil {
		return nil, fmt.Errorf("marshal Gemini request: %w", err)
	}

	resp, err := doGEMINIRequest(ctx, http.DefaultClient, body, apiKey)
	if err != nil {
		return nil, fmt.Errorf("do Gemini request: %w", err)
	}

	ch := make(chan string)
	go readGeminiSSEToChannel(resp, ch)
	return ch, nil
}
