package services

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"llm-system-interface/models"
	"log"
	"net/http"
	"os" // for os.Getenv to read environment variables
	"strings"
)

/**
validateUnmarshal parses a single Gemini SSE "data:" JSON payload and extracts text content.
It validates the nested Candidates > Content > Parts > Text structure and returns true only if
text is successfully extracted and non-empty. On failure, it logs the reason and returns false.
The extracted text is written to the provided pointer; callers must pass a valid *string.
*/
func validateUnmarshal(data string, text *string) bool {
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
		return false
	}

	if len(chunk.Candidates) == 0 || len(chunk.Candidates[0].Content.Parts) == 0 {
		log.Println("StreamLLM: no candidates or parts in chunk")
		return false
	}

	*text = strings.TrimSpace(chunk.Candidates[0].Content.Parts[0].Text)
	if *text == "" {
		log.Println("StreamLLM: empty text chunk")
		return false
	}
	return true
}

/**
readGeminiSSEToChannel reads the Gemini streaming HTTP response line by line,
filters for "data:" SSE events, validates each payload via validateUnmarshal,
and sends successfully parsed text chunks to ch. Both resp.Body and ch are closed
(via defer) when the scanner reaches EOF or errors, allowing receiver to detect stream end.
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
		data := strings.TrimPrefix(line, "data: ")

		text := ""
		if !validateUnmarshal(data, &text) { continue }

		log.Printf("StreamLLM: sending chunk=%q", text) // debug, remove later
		ch <- text
	}
}

/**
doGEMINIRequest builds and performs an HTTP POST to the Gemini API streaming endpoint.
It constructs the request with the provided body and API key, sets required headers,
and returns either the open response (caller must close) or an error if the request
fails or returns a non-200 status. The client parameter allows injection of a mock
for testing; in production, pass http.DefaultClient.
*/
func doGEMINIRequest(ctx context.Context, client *http.Client, body []byte, apiKey string) (*http.Response, error) {
	// 2.5: Free limits (realistic) ~100–1000 requests/day, ~5–15 requests/min, Sometimes ~250/day typical: use this in prod?
	// url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?alt=sse"
	// url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:streamGenerateContent?alt=sse"
	url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:streamGenerateContent?alt=sse"
	httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("build Gemini request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("x-goog-api-key", apiKey)

	resp, err := client.Do(httpReq)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		defer resp.Body.Close()
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("Gemini HTTP %d: %s", resp.StatusCode, strings.TrimSpace(string(respBody)))
	}
	return resp, nil
}

/**
tutorial: context.Context "A request bubble that travels through all your functions, telling them 'stop working if I get cancelled' and 'here's some shared data.'" Cancellation propagation – If a client disconnects or a timeout expires, all goroutines using that context know to stop immediately
Timeout management – Enforce "this entire operation must complete in 5 seconds"
Avoid resource leaks – No hanging goroutines waiting forever
Request tracking – Pass request IDs, user info, or other metadata down the call stack
type Context interface {
    Deadline() (deadline time.Time, ok bool)    // When should this context stop?
    Done() <-chan struct{}                       // Signal channel: closes when cancelled
    Err() error                                  // Why was it cancelled? (ctx.Canceled or ctx.DeadlineExceeded)
    Value(key interface{}) interface{}           // Get a stored value by key
}
*/
/**
StreamLLM orchestrates a streaming LLM request to the Gemini API.
It validates the API key, marshals the prompt into Gemini's JSON format, calls doGEMINIRequest,
launches readGeminiSSEToChannel in a non-blocking goroutine, and returns a read-only channel
of text chunks. Callers should iterate over the returned channel to receive streamed output.
On error (missing key, marshal failure, HTTP error), returns nil channel and error.

TODO: Implement app-side limits: max prompt size per request, per-user daily quota, and
consider summarized history instead of sending full conversation each time.
*/
func StreamLLM(ctx context.Context, req models.TextRequest) (<-chan string, error) {
	ch := make(chan string)
	apiKey := os.Getenv("GEMINI_API_KEY")

	if apiKey == "" {
		return nil, fmt.Errorf("GEMINI_API_KEY is not set in environment")
	}
	body, err := json.Marshal(map[string]any{  //// Gemini-specific JSON structure
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
	resp, err := doGEMINIRequest(ctx, http.DefaultClient, body, apiKey)
	if err != nil {
		return nil, fmt.Errorf("do Gemini request: %w", err)
	}
	go readGeminiSSEToChannel(resp, ch)
	return ch, nil
}
