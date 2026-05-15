package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"llm-system-interface/models"
	"net/http"
	"os"
	"strings"
)

func pyRagURL() string {
	v := os.Getenv("PY_RAG_URL")
	if strings.TrimSpace(v) == "" {
		return "http://python-rag:8090"
	}
	return strings.TrimRight(v, "/")
}

func ollamaURL() string {
	v := os.Getenv("OLLAMA_URL")
	if strings.TrimSpace(v) == "" {
		return "http://ollama:11434"
	}
	return strings.TrimRight(v, "/")
}

func chatModelName() string {
	v := os.Getenv("OLLAMA_MODEL")
	if strings.TrimSpace(v) == "" {
		return "gemma3:4b"
	}
	return v
}

// extractAnswer pulls the "A: ..." portion from "Q: ...\nA: ..." formatted text.
//
// Theory: docs are formatted by Python's embedder.format_doc() as
//   "Q: {question}\nA: {answer}"  or  "Q: ...\nA: ...\ntags: ..."
// The Q: line helped retrieve the doc but is redundant in the prompt — dropping
// it saves ~40-60% of context tokens, directly speeding up per-token generation.
//
// Falls back to full text if the separator is missing (malformed/legacy docs).
// Strips the "\ntags: ..." suffix which was added for embedding quality only.
//
// Edge cases:
//   - No "\nA: " → return full text (safe fallback, no crash)
//   - Empty answer after split → return full text
//   - Tags suffix → stripped before return
func extractAnswer(text string) string {
	const sep = "\nA: "
	idx := strings.Index(text, sep)
	if idx == -1 {
		return text // unknown format — safe fallback
	}
	answer := text[idx+len(sep):]

	// Strip tags suffix added for embedding signal, not for LLM consumption.
	if tagIdx := strings.Index(answer, "\ntags: "); tagIdx != -1 {
		answer = answer[:tagIdx]
	}
	answer = strings.TrimSpace(answer)
	if answer == "" {
		return text // empty answer → fallback to full text
	}
	return answer
}

// doJSON sends a JSON request and decodes the response into out (nil to discard).
func doJSON(ctx context.Context, method, url string, in any, out any) error {
	b, err := json.Marshal(in)
	if err != nil {
		return fmt.Errorf("marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, method, url, bytes.NewReader(b))
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("http %d from %s", resp.StatusCode, url)
	}
	if out == nil {
		return nil
	}
	if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
		return fmt.Errorf("unmarshal response: %w", err)
	}
	return nil
}

// doJSONWithRetry is like doJSON but retries on network errors and transient
// HTTP failures using withRetry.
//
// Why not reuse doJSON: http.Request.Body is an io.Reader — once read it is
// exhausted and cannot be replayed. Each retry must construct a fresh request
// with a new bytes.NewReader over the same marshalled bytes.
//
// Theory — why retries fix "connection refused" after python-rag restart:
//   Go's http.DefaultTransport keeps idle TCP connections in a pool.
//   After python-rag restarts it gets a new Docker-internal IP. The pooled
//   connection to the old IP gets a RST and fails immediately. withRetry
//   catches the network error, waits 1s, and creates a new TCP connection.
//   Docker's embedded DNS resolver returns the new container IP on the fresh
//   DNS lookup, so the retry succeeds.
//
// Edge cases:
//   - python-rag mid-startup (~2min): retries 1-3 will all fail; caller gets
//     a clean error ("community posts not available"). User can retry manually.
//   - ctx cancelled: withRetry propagates ctx.Done() immediately.
func doJSONWithRetry(ctx context.Context, method, url string, in any, out any) error {
	b, err := json.Marshal(in)
	if err != nil {
		return fmt.Errorf("marshal request: %w", err)
	}

	resp, err := withRetry(ctx, func() (*http.Response, error) {
		// Fresh reader on every attempt — bytes.NewReader is rewindable
		// because we hold the full slice, not a stream.
		req, err := http.NewRequestWithContext(ctx, method, url, bytes.NewReader(b))
		if err != nil {
			return nil, fmt.Errorf("build request: %w", err)
		}
		req.Header.Set("Content-Type", "application/json")
		return http.DefaultClient.Do(req)
	})
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("http %d from %s", resp.StatusCode, url)
	}
	if out == nil {
		return nil
	}
	if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
		return fmt.Errorf("unmarshal response: %w", err)
	}
	return nil
}

// StreamRagAnswer retrieves community contexts from the Python RAG service,
// builds a grounded prompt, and streams Gemma's answer token by token.
func StreamRagAnswer(ctx context.Context, question string) (<-chan string, error) {
	question = strings.TrimSpace(question)
	if question == "" {
		return nil, fmt.Errorf("question is required")
	}

	var retrieved models.RagRetrieveResponse
	if err := doJSONWithRetry(ctx, http.MethodPost, pyRagURL()+"/rag/retrieve",
		map[string]any{"question": question}, &retrieved); err != nil {
		return nil, fmt.Errorf("retrieve contexts: %w", err)
	}

	// Build answer-only context blocks.
	// extractAnswer strips the "Q: ..." prefix (retrieval metadata, redundant here).
	blocks := make([]string, len(retrieved.Contexts))
	for i, c := range retrieved.Contexts {
		blocks[i] = fmt.Sprintf("[%d] %s", i+1, extractAnswer(c.Text))
	}

	ctxStr := "(no context retrieved)"
	if len(blocks) > 0 {
		ctxStr = strings.Join(blocks, "\n\n")
	}

	prompt := "You are a peer assistant for School 42.\n" +
		"Answer ONLY from the community posts below.\n" +
		"Do not use any knowledge outside these posts.\n" +
		"If the posts do not contain enough to answer, reply with exactly:\n" +
		"\"The community hasn't covered this yet \xe2\x80\x94 be the first to post it!\"\n\n" +
		"Community posts:\n---\n" + ctxStr + "\n\n" +
		"Question: " + question

	body, err := json.Marshal(map[string]any{
		"model":  chatModelName(),
		"stream": true,
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
	})
	if err != nil {
		return nil, fmt.Errorf("marshal ollama request: %w", err)
	}

	resp, err := withRetry(ctx, func() (*http.Response, error) {
		req, err := http.NewRequestWithContext(ctx, http.MethodPost, ollamaURL()+"/api/chat", bytes.NewReader(body))
		if err != nil {
			return nil, err
		}
		req.Header.Set("Content-Type", "application/json")
		return http.DefaultClient.Do(req)
	})
	if err != nil {
		return nil, fmt.Errorf("ollama stream: %w", err)
	}

	ch := make(chan string)
	go readOllamaToChannel(ctx, resp, ch)
	return ch, nil
}
