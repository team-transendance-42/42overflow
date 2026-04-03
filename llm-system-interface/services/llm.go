package services

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"llm-system-interface/models"
	"net/http"
	"os" // for os.Getenv to read environment variables
	"strings"
	"io"
	"log"
)
// TODO: Keep your own app-side limits: max prompt size, per-student daily quota, and maybe summarized history instead of sending full history each time
func StreamLLM(ctx context.Context, req models.TextRequest) (<-chan string, error) {
	ch := make(chan string)
	apiKey := os.Getenv("GEMINI_API_KEY")

    if apiKey == "" {
        return nil, fmt.Errorf("GEMINI_API_KEY is not set in environment")
    }

	// 1. Gemini-specific JSON structure
    body, err := json.Marshal(map[string]any{
        "contents": []map[string]any{
            {
                "parts": []map[string]string{
                    {"text": req.Prompt},
                },
            },
        },
    })
	if err != nil {
		return nil, fmt.Errorf("marshal Gemini request: %w", err)
	}
    // We use "gemini-1.5-flash" as it's the standard for the free tier
    // url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?alt=sse"
	url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:streamGenerateContent?alt=sse" // CHEAPEST?
    httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("build Gemini request: %w", err)
	}
    httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("x-goog-api-key", apiKey)

    resp, err := http.DefaultClient.Do(httpReq)
    if err != nil { return nil, err}
	if resp.StatusCode != http.StatusOK {
		defer resp.Body.Close()
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("Gemini HTTP %d: %s", resp.StatusCode, strings.TrimSpace(string(respBody)))
	}

	go func() {
		defer close(ch)
		defer resp.Body.Close()
		scanner := bufio.NewScanner(resp.Body)
        for scanner.Scan() {
            line := scanner.Text()
            if !strings.HasPrefix(line, "data: ") {
                continue
            }
            data := strings.TrimPrefix(line, "data: ")

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
				log.Printf("StreamLLM: unmarshal failed: %v, data=%q", err, data)
				continue
			}

			if len(chunk.Candidates) == 0 {
				log.Println("StreamLLM: no candidates")
				continue
			}
			if len(chunk.Candidates[0].Content.Parts) == 0 {
				log.Println("StreamLLM: no parts")
				continue
			}

			text := strings.TrimSpace(chunk.Candidates[0].Content.Parts[0].Text)
			if text == "" {
				log.Println("StreamLLM: empty text chunk")
				continue
			}

			log.Printf("StreamLLM: sending chunk=%q", text)
			ch <- text
		}
	}()
	return ch, nil
}