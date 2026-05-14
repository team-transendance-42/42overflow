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

// StreamRagAnswer retrieves community contexts from the Python RAG service,
// builds a grounded prompt, and streams Gemma's answer token by token.
// Returns: token channel, plain-text context strings (for sources panel), confidence score, error.
func StreamRagAnswer(ctx context.Context, question string) (<-chan string, []string, float64, error) {
	question = strings.TrimSpace(question)
	if question == "" {
		return nil, nil, 0, fmt.Errorf("question is required")
	}

	var retrieved models.RagRetrieveResponse
	if err := doJSON(ctx, http.MethodPost, pyRagURL()+"/rag/retrieve",
		map[string]any{"question": question}, &retrieved); err != nil {
		return nil, nil, 0, fmt.Errorf("retrieve contexts: %w", err)
	}

	texts := make([]string, len(retrieved.Contexts))
	blocks := make([]string, len(retrieved.Contexts))
	for i, c := range retrieved.Contexts {
		texts[i] = c.Text
		blocks[i] = fmt.Sprintf("[%d] %s", i+1, c.Text)
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
		return nil, texts, retrieved.Confidence, fmt.Errorf("marshal ollama request: %w", err)
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
		return nil, texts, retrieved.Confidence, fmt.Errorf("ollama stream: %w", err)
	}

	ch := make(chan string)
	go readOllamaToChannel(ctx, resp, ch)
	return ch, texts, retrieved.Confidence, nil
}
