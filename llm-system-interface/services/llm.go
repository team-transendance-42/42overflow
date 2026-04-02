package services

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"strings"
	"llm-system-interface/models"
)

func StreamLLM(ctx context.Context, req models.TextRequest) (<-chan string, error) {
	ch := make(chan string)

	// Marshal the request body (not used for now)
	_, err := json.Marshal(map[string]any{
		"model": req.Model,
		"stream": true,
		"messages": []map[string]string{
			{"role": "user", "content": req.Prompt},
		},
	})
	if err != nil {
		return nil, err
	}

	// NOTE: API key and actual request commented out for now
	// httpReq, err := http.NewRequestWithContext(ctx, "POST", "https://api.openai.com/v1/chat/completions", bytes.NewReader(body))
	// if err != nil {
	// 	return nil, err
	// }
	// httpReq.Header.Set("Authorization", "Bearer "+apiKey)
	// httpReq.Header.Set("Content-Type", "application/json")

	// resp, err := http.DefaultClient.Do(httpReq)
	// if err != nil {
	// 	return nil, err
	// }

	go func() {
		defer close(ch)
		// defer resp.Body.Close()

		// Simulate streaming chunks for demonstration
		chunks := []string{"This ", "is ", "a ", "test."}
		for _, chunk := range chunks {
			ch <- chunk
		}
	}()

	return ch, nil
}