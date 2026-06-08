package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

const defaultRagCollection = "my_rag_collection"

func ragBackend() string {
	v := strings.ToLower(strings.TrimSpace(os.Getenv("RAG_BACKEND")))
	if v == "" {
		return "go"
	}
	return v
}

func pyRagURL() string {
	v := os.Getenv("PY_RAG_URL")
	if strings.TrimSpace(v) == "" {
		return "http://python-rag:8090"
	}
	return strings.TrimRight(v, "/")
}

func usePythonRag() bool {
	return ragBackend() == "python"
}

func chromaURL() string {
	v := os.Getenv("CHROMA_URL")
	if strings.TrimSpace(v) == "" {
		return "http://chromadb:8000"
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

func ragCollectionName(name string) string {
	name = strings.TrimSpace(name)
	if name == "" {
		return defaultRagCollection
	}
	return name
}

func embedModelName() string {
	v := os.Getenv("OLLAMA_EMBED_MODEL")
	if strings.TrimSpace(v) == "" {
		return "nomic-embed-text"
	}
	return v
}

func chatModelName() string {
	v := os.Getenv("OLLAMA_MODEL")
	if strings.TrimSpace(v) == "" {
		return "gemma3:4b"
	}
	return v
}

func doJSON(ctx context.Context, method, url string, in any, out any) error {
	var body io.Reader
	if in != nil {
		b, err := json.Marshal(in)
		if err != nil {
			return fmt.Errorf("marshal request: %w", err)
		}
		body = bytes.NewReader(b)
	}

	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("http %d: %s", resp.StatusCode, strings.TrimSpace(string(respBody)))
	}
	if out == nil || len(respBody) == 0 {
		return nil
	}
	if err := json.Unmarshal(respBody, out); err != nil {
		return fmt.Errorf("unmarshal response: %w", err)
	}
	return nil
}

func ensureCollection(ctx context.Context, collection string) error {
	payload := map[string]any{
		"name":          collection,
		"get_or_create": true,
	}
	return doJSON(ctx, http.MethodPost, chromaURL()+"/api/v1/collections", payload, nil)
}

func embedTexts(ctx context.Context, texts []string) ([][]float64, error) {
	if len(texts) == 0 {
		return nil, fmt.Errorf("no texts to embed")
	}

	payload := map[string]any{
		"model": embedModelName(),
		"input": texts,
	}

	var resp struct {
		Embeddings [][]float64 `json:"embeddings"`
		Embedding  []float64   `json:"embedding"`
	}
	if err := doJSON(ctx, http.MethodPost, ollamaURL()+"/api/embed", payload, &resp); err != nil {
		return nil, err
	}

	if len(resp.Embeddings) > 0 {
		return resp.Embeddings, nil
	}
	if len(resp.Embedding) > 0 {
		return [][]float64{resp.Embedding}, nil
	}
	return nil, fmt.Errorf("empty embeddings response")
}

func IndexDocuments(ctx context.Context, collection string, documents []string) (int, error) {
	collection = ragCollectionName(collection)

	filtered := make([]string, 0, len(documents))
	for _, d := range documents {
		d = strings.TrimSpace(d)
		if d != "" {
			filtered = append(filtered, d)
		}
	}
	if len(filtered) == 0 {
		return 0, fmt.Errorf("documents are required")
	}

	if usePythonRag() {
		var resp struct {
			Indexed int `json:"indexed"`
		}
		payload := map[string]any{
			"collection": collection,
			"documents":  filtered,
		}
		if err := doJSON(ctx, http.MethodPost, pyRagURL()+"/rag/index", payload, &resp); err != nil {
			return 0, fmt.Errorf("python rag index: %w", err)
		}
		if resp.Indexed > 0 {
			return resp.Indexed, nil
		}
		return len(filtered), nil
	}

	if err := ensureCollection(ctx, collection); err != nil {
		return 0, fmt.Errorf("ensure collection: %w", err)
	}

	embeds, err := embedTexts(ctx, filtered)
	if err != nil {
		return 0, fmt.Errorf("embed documents: %w", err)
	}
	if len(embeds) != len(filtered) {
		return 0, fmt.Errorf("embedding count mismatch: docs=%d embeddings=%d", len(filtered), len(embeds))
	}

	ids := make([]string, 0, len(filtered))
	for i := range filtered {
		ids = append(ids, fmt.Sprintf("doc-%d", i+1))
	}

	payload := map[string]any{
		"ids":        ids,
		"documents":  filtered,
		"embeddings": embeds,
	}
	url := fmt.Sprintf("%s/api/v1/collections/%s/upsert", chromaURL(), collection)
	if err := doJSON(ctx, http.MethodPost, url, payload, nil); err != nil {
		return 0, fmt.Errorf("upsert docs: %w", err)
	}
	return len(filtered), nil
}

func queryContexts(ctx context.Context, collection, question string, topK int) ([]string, error) {
	if topK <= 0 {
		topK = 3
	}

	embeds, err := embedTexts(ctx, []string{question})
	if err != nil {
		return nil, fmt.Errorf("embed question: %w", err)
	}

	payload := map[string]any{
		"query_embeddings": embeds,
		"n_results":        topK,
	}
	url := fmt.Sprintf("%s/api/v1/collections/%s/query", chromaURL(), collection)

	var resp struct {
		Documents [][]string `json:"documents"`
	}
	if err := doJSON(ctx, http.MethodPost, url, payload, &resp); err != nil {
		return nil, fmt.Errorf("chroma query: %w", err)
	}
	if len(resp.Documents) == 0 {
		return []string{}, nil
	}
	return resp.Documents[0], nil
}

func askOllama(ctx context.Context, prompt string) (string, error) {
	payload := map[string]any{
		"model":  chatModelName(),
		"stream": false,
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
	}

	var resp struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	}
	if err := doJSON(ctx, http.MethodPost, ollamaURL()+"/api/chat", payload, &resp); err != nil {
		return "", fmt.Errorf("ollama chat: %w", err)
	}
	if strings.TrimSpace(resp.Message.Content) == "" {
		return "", fmt.Errorf("empty model answer")
	}
	return resp.Message.Content, nil
}

func AskRag(ctx context.Context, collection, question string, topK int) (string, []string, error) {
	collection = ragCollectionName(collection)
	question = strings.TrimSpace(question)
	if question == "" {
		return "", nil, fmt.Errorf("question is required")
	}

	if usePythonRag() {
		var resp struct {
			Answer   string   `json:"answer"`
			Contexts []string `json:"contexts"`
		}
		payload := map[string]any{
			"collection": collection,
			"question":   question,
			"top_k":      topK,
		}
		if err := doJSON(ctx, http.MethodPost, pyRagURL()+"/rag/ask", payload, &resp); err != nil {
			return "", nil, fmt.Errorf("python rag ask: %w", err)
		}
		if strings.TrimSpace(resp.Answer) == "" {
			return "", resp.Contexts, fmt.Errorf("empty model answer")
		}
		return resp.Answer, resp.Contexts, nil
	}

	contexts, err := queryContexts(ctx, collection, question, topK)
	if err != nil {
		return "", nil, err
	}

	ctxText := "No context found."
	if len(contexts) > 0 {
		ctxText = strings.Join(contexts, "\n---\n")
	}

	prompt := "Use the context below to answer. If context is missing, say you are unsure briefly.\n\n" +
		"Context:\n" + ctxText + "\n\nQuestion:\n" + question

	answer, err := askOllama(ctx, prompt)
	if err != nil {
		return "", contexts, err
	}
	return answer, contexts, nil
}
