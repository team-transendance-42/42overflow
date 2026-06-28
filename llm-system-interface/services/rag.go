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
//
//	"Q: {question}\nA: {answer}"  or  "Q: ...\nA: ...\ntags: ..."
//
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

/*
	 doJSONWithRetry is like doJSON but retries on network errors and transient
	 HTTP failures using withRetry.

	 Why not reuse doJSON: http.Request.Body is an io.Reader — once read it is
	 exhausted and cannot be replayed. Each retry must construct a fresh request
	 with a new bytes.NewReader over the same marshalled bytes.

	 Theory — why retries fix "connection refused" after python-rag restart:

		Go's http.DefaultTransport keeps idle TCP connections in a pool.
		After python-rag restarts it gets a new Docker-internal IP. The pooled
		connection to the old IP gets a RST and fails immediately. withRetry
		catches the network error, waits 1s, and creates a new TCP connection.
		Docker's embedded DNS resolver returns the new container IP on the fresh
		DNS lookup, so the retry succeeds.

	 Edge cases:
	   - python-rag mid-startup (~2min): retries 1-3 will all fail; caller gets
	     a clean error ("community posts not available"). User can retry manually.
	   - ctx cancelled: withRetry propagates ctx.Done() immediately.
*/
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

/*
buildRAGPrompt builds the grounded prompt sent to Ollama.
Strict rules prevent hallucination: the model must ONLY use the provided
context and must not fall back to its training knowledge or guess.

Rule 1 says "reproduce the FULL answer" — small models (gemma3:4b) otherwise
interpret "answer clearly" as "be concise" and return only the first sentence.
*/
func buildRAGPrompt(ctxStr, question string) string {
	return "You are a 42 school tutor. Answer using ONLY the CONTEXT below. Reply thoroughly with all relevant info.\n" +
		"If the answer is not in the CONTEXT, reply EXACTLY: \"I am here to help with 42 curriculum questions only. How can I help you?\"\n" +
		"CONTEXT:\n" + ctxStr + "\n\n" +
		"QUESTION:\n" + question + "\n\n" +
		"ANSWER:"
}

/*
StreamRagAnswer retrieves community contexts from the Python RAG service,
builds a grounded prompt, and streams Gemma's answer token by token.
*/
func StreamRagAnswer(ctx context.Context, question string) (<-chan string, error) {
	question = strings.TrimSpace(question)
	if question == "" {
		return nil, fmt.Errorf("question is required")
	}

	if cached, ok := ragCacheGet(question); ok {
		log.Printf("[RAG] cache HIT for %q — len=%d", question, len(cached))
		ch := make(chan string, 1)
		ch <- cached
		close(ch)
		return ch, nil
	}
	log.Printf("[RAG] cache MISS for %q — calling python-rag", question)

	var retrieved models.RagRetrieveResponse
	if err := doJSONWithRetry(ctx, http.MethodPost, pyRagURL()+"/rag/retrieve",
		map[string]any{"question": question}, &retrieved); err != nil {
		return nil, fmt.Errorf("retrieve contexts: %w", err)
	}
	log.Printf("[RAG] retrieved %d contexts, confidence=%.4f, best_similarity=%.4f, has_embeddings=%v",
		len(retrieved.Contexts), retrieved.Confidence, retrieved.BestSimilarity, retrieved.HasEmbeddings)

	// Two-layer relevance gate — both must pass before Ollama is called.
	//
	// Layer 1 — RRF confidence (keyword signal):
	//   Pure-dense-only score (no BM25 term overlap) ≈ 1/60 = 0.0167.
	//   Catches greetings and gibberish where BM25 finds nothing at all.
	//
	// Layer 2 — cosine similarity (semantic signal):
	//   best_similarity is the raw cosine between the question embedding and
	//   the single closest doc across the full corpus (unfiltered, n=1 search).
	//   Unlike RRF, this measures actual meaning overlap, not retrieval agreement.
	//   "meaning of life" → cosine ≈ 0.12 vs any C/git doc → blocked.
	//   "what is malloc"  → cosine ≈ 0.80 vs malloc doc   → passes.
	//   Threshold 0.45 sits between unrelated (~0.10–0.30) and on-topic (~0.65–0.90).
	//   Tune by watching logs: docker compose logs llm-server -f
	const (
		minRagConfidence    = 0.020
		minCosineSimilarity = 0.55
	)
	noContext := func() (<-chan string, error) {
		ch := make(chan string, 1)
		ch <- "Hi! I can only help with 42 School project questions — ask me about your projects and I'll look through what other students have shared."
		close(ch)
		return ch, nil
	}
	if retrieved.Confidence < minRagConfidence {
		return noContext()
	}
	// Semantic gate: only applied when NumpyIndex was built at startup.
	// When has_embeddings=false (embedding service was down), best_similarity
	// is always 0.0 — applying the gate would block all queries. Fall back to
	// the RRF confidence gate alone, which still requires actual keyword overlap.
	if retrieved.HasEmbeddings && retrieved.BestSimilarity < minCosineSimilarity {
		return noContext()
	}

	// Tier 1: high-similarity match — skip Ollama, return stored answer verbatim.
	// Gemma3:4b truncates long answers even at temp 0.3; bypassing the LLM for
	// near-identical questions guarantees the full seed answer is returned.
	const directBypassSimilarity = 0.85
	if retrieved.HasEmbeddings && retrieved.BestSimilarity >= directBypassSimilarity && len(retrieved.Contexts) > 0 {
		answer := "From community: " + extractAnswer(retrieved.Contexts[0].Text)
		log.Printf("[RAG] direct answer (similarity=%.4f) — skipping Ollama", retrieved.BestSimilarity)
		ragCacheSet(question, answer)
		ch := make(chan string, 1)
		ch <- answer
		close(ch)
		return ch, nil
	}

	// Build answer-only context blocks.
	// extractAnswer strips the "Q: ..." prefix (retrieval metadata, redundant here).
	blocks := make([]string, len(retrieved.Contexts))
	for i, c := range retrieved.Contexts {
		extracted := extractAnswer(c.Text)
		log.Printf("[RAG] context[%d] raw_len=%d extracted_len=%d", i+1, len(c.Text), len(extracted))
		blocks[i] = fmt.Sprintf("[%d] %s", i+1, extracted)
	}

	ctxStr := "(no context retrieved)"
	if len(blocks) > 0 {
		ctxStr = strings.Join(blocks, "\n\n")
	}

	prompt := buildRAGPrompt(ctxStr, question)
	log.Printf("[RAG] prompt total_len=%d, sending to ollama model=%s", len(prompt), chatModelName())

	// DISABLED — Tier 2 (conditional): lower temperature only for similar matches. See doc-dev-rag.md.
	// ollamaReq := map[string]any{
	// 	"model":      chatModelName(),
	// 	"stream":     true,
	// 	"keep_alive": -1,
	// 	"messages": []map[string]string{
	// 		{"role": "user", "content": prompt},
	// 	},
	// }
	// if retrieved.HasEmbeddings {
	// 	ollamaReq["options"] = map[string]any{"temperature": 0.3}
	// }
	// body, err := json.Marshal(ollamaReq)

	// DISABLED — original: default Ollama temperature (0.8), higher randomness.
	// body, err := json.Marshal(map[string]any{
	// 	"model":      chatModelName(),
	// 	"stream":     true,
	// 	"keep_alive": -1,
	// 	"messages": []map[string]string{
	// 		{"role": "user", "content": prompt},
	// 	},
	// })

	// temperature 0.3 for all calls — more deterministic, reduces inconsistent answers.
	body, err := json.Marshal(map[string]any{
		"model":      chatModelName(),
		"stream":     true,
		"keep_alive": -1,
		"options":    map[string]any{"temperature": 0.3},
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
	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("ollama HTTP %d: %s", resp.StatusCode, strings.TrimSpace(string(respBody)))
	}

	rawCh := make(chan string)
	go readOllamaToChannel(ctx, resp, rawCh)

	outCh := make(chan string)
	go func() {
		defer close(outCh)
		var sb strings.Builder
		for chunk := range rawCh {
			sb.WriteString(chunk)
			outCh <- chunk
		}
		// Only cache when the stream completed naturally. If ctx was cancelled
		// (client disconnected), rawCh closes early with a partial answer —
		// caching it would serve a truncated response to the next N users for 1h.
		// Also skip "no info" responses so a /admin/sync-chroma that adds the
		// relevant data is not blocked by a stale cache entry for up to 1h.
		log.Printf("[RAG] ollama final answer len=%d: %q", sb.Len(), sb.String())
		const noInfoMarker = "I am here to help with 42 curriculum questions only"
		if ctx.Err() == nil && !strings.Contains(sb.String(), noInfoMarker) {
			ragCacheSet(question, sb.String())
		}
	}()
	return outCh, nil
}
