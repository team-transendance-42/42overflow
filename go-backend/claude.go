package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"
)

// ─────────────────────────────────────────────
//  CONFIG
// ─────────────────────────────────────────────

const (
	apiURL       = "https://api.anthropic.com/v1/messages"
	model        = "claude-sonnet-4-20250514"
	maxTokens    = 1024
	apiVersion   = "2023-06-01"

	// Rate limiting: max N requests per window
	rateLimitRequests = 5
	rateLimitWindow   = 60 * time.Second
)

// ─────────────────────────────────────────────
//  RATE LIMITER  (token-bucket style, simple)
// ─────────────────────────────────────────────

type RateLimiter struct {
	mu        sync.Mutex
	tokens    int
	max       int
	refillAt  time.Time
	window    time.Duration
}

func NewRateLimiter(maxReqs int, window time.Duration) *RateLimiter {
	return &RateLimiter{
		tokens:   maxReqs,
		max:      maxReqs,
		window:   window,
		refillAt: time.Now().Add(window),
	}
}

// Allow returns nil if the request is permitted, or an error with wait time.
func (r *RateLimiter) Allow() error {
	r.mu.Lock()
	defer r.mu.Unlock()

	// Refill bucket if the window has passed
	if time.Now().After(r.refillAt) {
		r.tokens = r.max
		r.refillAt = time.Now().Add(r.window)
	}

	if r.tokens <= 0 {
		wait := time.Until(r.refillAt).Round(time.Second)
		return fmt.Errorf("rate limit exceeded — try again in %s", wait)
	}

	r.tokens--
	return nil
}

// ─────────────────────────────────────────────
//  API REQUEST / RESPONSE TYPES
// ─────────────────────────────────────────────

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type RequestBody struct {
	Model     string    `json:"model"`
	MaxTokens int       `json:"max_tokens"`
	Messages  []Message `json:"messages"`
	Stream    bool      `json:"stream"`
}

// Non-streaming response
type ResponseBody struct {
	Content []struct { // []slice(dynamic arr) of of T(hhere struct)
		Text string `json:"text"` //json:"text" tells Go to map the JSON field "text" to this field.
	} `json:"content"`
	Error *APIError `json:"error,omitempty"` //If Error is nil, omit it from the JSON output.
}

// Streaming event (Server-Sent Events)
type StreamEvent struct {
	Type  string `json:"type"`
	Delta *struct { // anonym struct named Delta
		Type string `json:"type"`
		Text string `json:"text"`
	} `json:"delta,omitempty"`
	Error *APIError `json:"error,omitempty"`
}

type APIError struct {
	Type    string `json:"type"`
	Message string `json:"message"`
}

func (e *APIError) Error() string {
	return fmt.Sprintf("API error [%s]: %s", e.Type, e.Message)
}

// ─────────────────────────────────────────────
//  LLM CLIENT
// ─────────────────────────────────────────────

type LLMClient struct {
	apiKey      string
	httpClient  *http.Client
	rateLimiter *RateLimiter
}

func NewLLMClient(apiKey string) *LLMClient {
	return &LLMClient{
		apiKey: apiKey,
		httpClient: &http.Client{
			Timeout: 120 * time.Second, // long timeout for slow completions
		},
		rateLimiter: NewRateLimiter(rateLimitRequests, rateLimitWindow),
	}
}

//creates a HTTP POST to the Anthropic messages endpoint.
func (c *LLMClient) buildRequest(messages []Message, stream bool) (*http.Request, error) {
	body := RequestBody{
		Model:     model,
		MaxTokens: maxTokens,
		Messages:  messages,
		Stream:    stream,
	}

	data, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("failed to encode request: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, apiURL, bytes.NewReader(data))
	if err != nil {
		return nil, fmt.Errorf("failed to build request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", c.apiKey)
	req.Header.Set("anthropic-version", apiVersion)

	return req, nil
}

// ─── NON-STREAMING ────────────────────────────

// Generate sends a prompt and returns the full response text.
func (c *LLMClient) Generate(prompt string) (string, error) {
	// 1. Check rate limit
	if err := c.rateLimiter.Allow(); err != nil {
		return "", err
	}

	messages := []Message{{Role: "user", Content: prompt}}

	req, err := c.buildRequest(messages, false)
	if err != nil {
		return "", err
	}

	// 2. Send request
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("network error: %w", err)
	}
	defer resp.Body.Close()

	// 3. Handle HTTP-level errors
	if err := checkHTTPStatus(resp); err != nil {
		return "", err
	}

	// 4. Parse response
	var result ResponseBody
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("failed to decode response: %w", err)
	}

	if result.Error != nil {
		return "", result.Error
	}
	if len(result.Content) == 0 {
		return "", errors.New("empty response from API")
	}

	return result.Content[0].Text, nil
}

// ─── STREAMING ────────────────────────────────

// GenerateStream sends a prompt and streams tokens to stdout as they arrive.
func (c *LLMClient) GenerateStream(prompt string) error {
	// 1. Rate limit
	if err := c.rateLimiter.Allow(); err != nil {
		return err
	}

	messages := []Message{{Role: "user", Content: prompt}}

	req, err := c.buildRequest(messages, true)
	if err != nil {
		return err
	}

	// 2. Send
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("network error: %w", err)
	}
	defer resp.Body.Close()

	if err := checkHTTPStatus(resp); err != nil {
		return err
	}

	// 3. Read Server-Sent Events line by line
	//    Each event looks like:
	//      data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Hello"}}
	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		line := scanner.Text()

		// SSE lines that carry data start with "data: "
		if !strings.HasPrefix(line, "data: ") {
			continue
		}

		payload := strings.TrimPrefix(line, "data: ")

		// Stream end sentinel
		if payload == "[DONE]" {
			break
		}

		var event StreamEvent
		if err := json.Unmarshal([]byte(payload), &event); err != nil {
			// Skip malformed lines rather than crashing
			continue
		}

		// Surface API-level errors embedded in the stream
		if event.Error != nil {
			return event.Error
		}

		// Print the text delta immediately (no newline — tokens are mid-sentence)
		if event.Type == "content_block_delta" && event.Delta != nil {
			fmt.Print(event.Delta.Text)
		}
	}

	fmt.Println() // newline after stream ends

	if err := scanner.Err(); err != nil && !errors.Is(err, io.EOF) {
		return fmt.Errorf("stream read error: %w", err)
	}

	return nil
}

// ─────────────────────────────────────────────
//  HTTP STATUS HELPER
// ─────────────────────────────────────────────

func checkHTTPStatus(resp *http.Response) error {
	switch resp.StatusCode {
	case http.StatusOK:
		return nil
	case http.StatusUnauthorized:
		return errors.New("invalid API key (401) — set ANTHROPIC_API_KEY")
	case http.StatusTooManyRequests:
		retryAfter := resp.Header.Get("Retry-After")
		if retryAfter != "" {
			return fmt.Errorf("server-side rate limit hit (429) — retry after %s s", retryAfter)
		}
		return errors.New("server-side rate limit hit (429) — slow down")
	case http.StatusBadRequest:
		return errors.New("bad request (400) — check your prompt or model name")
	case http.StatusInternalServerError, http.StatusServiceUnavailable:
		return fmt.Errorf("Anthropic server error (%d) — try again later", resp.StatusCode)
	default:
		return fmt.Errorf("unexpected HTTP status: %d", resp.StatusCode)
	}
}

// ─────────────────────────────────────────────
//  INTERACTIVE CLI
// ─────────────────────────────────────────────

// The main function and CLI logic have been removed.