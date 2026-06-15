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

/* safely pulls the text string out of a Gemini API streaming chunk
JSON can't be used directly in Go. needs a Go struct that mirrors the JSON shape so json.Unmarshal knows where to put each value.
json looks like:
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Hello, how can I help?"
          }
chunk          → the whole parsed JSON object
chunk.Candidates        → the "candidates" array
chunk.Candidates[0]     → first candidate
chunk.Candidates[0].Content.Parts[0].Text  → the actual text string
Candidates, Content, Parts, Text are capitalized because json.Unmarshal needs to access them to write values into them. It uses Go's reflection system, which can only see exported (capital) fields

json.Unmarshal requires []byte(array of bytes, where each byte is a number 0–255.), not string. That's just how the Go standard library designed it — because JSON is fundamentally raw bytes (it could come from a file, network, etc.), not just text.
text *string — a pointer to write the result into (one string)
*/
func extractTextFromJSON(data string, text *string) bool {
	var chunk struct {
		Candidates []struct { // a field in chunk var
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

/*
resp.Body — an io.ReadCloser (HTTP response stream from Gemini's server)
ch — a chan string (Go channel between goroutines)
*/
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
	if err := scanner.Err(); err != nil {
		log.Printf("readGeminiSSEToChannel: scanner error: %v", err)
		ch <- models.StreamErrSentinel + err.Error()
	}
}

func doGEMINIRequest(ctx context.Context, client *http.Client, body []byte, apiKey string) (*http.Response, error) {
	url := os.Getenv("GEMINI_URL")
	model := os.Getenv("GEMINI_MODEL")
	if model == "" || url == "" {
		return nil, fmt.Errorf("GEMINI_URL and GEMINI_MODEL must be set")
	}

	return withRetry(ctx, func() (*http.Response, error) {
		httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
		if err != nil {
			return nil, fmt.Errorf("build Gemini request: %w", err)
		}
		httpReq.Header.Set("Content-Type", "application/json") // Tells Gemini "the body I'm sending is JSON format"
		httpReq.Header.Set("x-goog-api-key", apiKey) // Authentication — proves you have permission to use the API, without it: 403
		return client.Do(httpReq)
	})
}

/*
the func is just a format adapter:
app uses "assistant" (OpenAI convention), Gemini expects "model". Simple rename.
This is a common pattern called a DTO (Data Transfer Object) — you keep your internal representation clean and convert at the boundary when talking to external APIs
Gemini doesn't have a content field — it uses parts (because it supports multimodal: text, images, etc. as separate parts)
*/
func buildGeminiContents(msgs []models.Message) []map[string]any {
	contents := make([]map[string]any, 0, len(msgs)) // built-in for creating slices, maps, channels
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
	const maxMessages = 5 // keep history up to the last maxMessages
	msgs := make([]models.Message, 0, len(req.Messages)+1)
	msgs = append(msgs, req.Messages...)

	if strings.TrimSpace(req.Prompt) != "" {
		msgs = append(msgs, models.Message{
			Role:    "user",
			Content: req.Prompt,
		})
	}

	if len(msgs) > maxMessages {
		msgs = msgs[len(msgs)-maxMessages:] // msgs[1:]
	}

	return buildGeminiContents(msgs)
}

/**
Channel — typed pipe between goroutines: without shared memory + mutexes
ch := make(chan int)       // unbuffered: sender blocks until receiver reads
ch := make(chan int, 5)    // buffered: sender can push 5 items before blocking
*/
/*
builds an HTTP POST request to the Gemini API with the provided body as JSON
Sets the Content-Type and x-goog-api-key headers.
Sends the request using the provided http.Client.
Returns the HTTP response or an error
!!NB!!
After readGeminiSSEToChannel finishes and closes the channel, the caller can still receive all values sent before closing, but cannot send to the channel. The sending side (inside the goroutine) is done and closed; the receiving side (the caller) can keep reading until the channel is empty and closed.
*/
func StreamLLM(ctx context.Context, req models.TextRequest) (<-chan string, error) {
	const geminiSystemPrompt = "reply with less words, dont repeat info"
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
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		return nil, fmt.Errorf("gemini HTTP %d", resp.StatusCode)
	}

	ch := make(chan string)
	go readGeminiSSEToChannel(resp, ch)
	return ch, nil
}
