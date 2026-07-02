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

/*
we get text: 'Q:..\nA:..'; we want to save tokens, so take only A:
*/
func extractAnswer(text string) string {
	_, answer, found := strings.Cut(text, "\nA: ")
	if !found {
		return text // unknown format — safe fallback
	}
	// tags suffix is used for embedding signal, not for LLM consumption.
	if before, _, ok := strings.Cut(answer, "\ntags: "); ok {
		answer = before
	}
	answer = strings.TrimSpace(answer)
	if answer == "" {
		return text
	}
	return answer
}

/*
sends a JSON HTTP request with automatic retry logic
out must be a pointer (e.g. &myStruct) — json.Decode silently does nothing if it isn't
*/
func ragAdminToken() string {
	return os.Getenv("RAG_ADMIN_TOKEN")
}

func doJSONWithRetry(ctx context.Context, method, url string, in any, out any, extraHeaders map[string]string) error {
	b, err := json.Marshal(in)
	if err != nil {
		return fmt.Errorf("marshal request: %w", err)
	}

	resp, err := withRetry(ctx, func() (*http.Response, error) {
		/* Fresh reader on every attempt — bytes.NewReader is rewindable
		because we hold the full slice, not a stream.
		*/
		req, err := http.NewRequestWithContext(ctx, method, url, bytes.NewReader(b))
		if err != nil {
			return nil, fmt.Errorf("build request: %w", err)
		}
		req.Header.Set("Content-Type", "application/json")
		for k, v := range extraHeaders {
			req.Header.Set(k, v)
		}
		return http.DefaultClient.Do(req)
	})
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		// Drain before close so the Transport can reuse the TCP connection.
		_, _ = io.Copy(io.Discard, resp.Body)
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
Strict rules prevent hallucination: the model must ONLY use the provided
context and must not fall back to its training knowledge or guess.
Rule 1 says "reproduce the FULL answer" — small models (gemma3:4b) otherwise
interpret "answer clearly" as "be concise" and return only the first sentence.
*/
func buildRAGPrompt(ctxStr, question string) string {
	return "You are a 42 school tutor. Answer using ONLY the CONTEXT below. Reply thoroughly with all relevant info.\n" +
		"If the answer is not in the CONTEXT, reply EXACTLY: \"I am here to help with 42 curriculum questions only. Shoot :)\"\n" +
		"CONTEXT:\n" + ctxStr + "\n\n" +
		"QUESTION:\n" + question + "\n\n" +
		"ANSWER:"
}

const (
	minRagConfidence       = 0.020
	minCosineSimilarity    = 0.55
	/* 0.82 instead of 0.85: questions with similarity in the 0.82–0.85 range
	 have the correct top-1 doc but gemma3:4b still returns the fallback.
	 Raise back to 0.85 if a better model handles those cases correctly.
	 */
	directBypassSimilarity = 0.85
)

/* ForwardAndAccumulate reads chunks from rawCh, forwards each to outCh, and calls
 onDone with the full accumulated text when rawCh drains naturally. If ctx is
 cancelled, forwarding and caching stop but rawCh is still fully drained —
 returning early would block readOllamaToChannel on its unbuffered send and leak
 the goroutine + resp.Body.
 */
func ForwardAndAccumulate(ctx context.Context, rawCh <-chan string, outCh chan<- string, onDone func(string)) {
	defer close(outCh)
	var sb strings.Builder
	cancelled := false
	for chunk := range rawCh {
		if cancelled {
			continue // drain without forwarding to unblock the producer
		}
		sb.WriteString(chunk)
		select {
		case outCh <- chunk:
		case <-ctx.Done():
			cancelled = true // stop forwarding; keep ranging to drain rawCh
		}
	}
	if !cancelled && ctx.Err() == nil {
		onDone(sb.String())
	}
}

// staticChan wraps a single text value in a buffered, closed channel.
// Used wherever the answer is already known and no streaming is needed.
func staticChan(text string) <-chan string {
	ch := make(chan string, 1)
	ch <- text
	close(ch)
	return ch
}

// fetchRAGContexts calls the Python /rag/retrieve endpoint and returns the response.
func fetchRAGContexts(ctx context.Context, question string) (models.RagRetrieveResponse, error) {
	var r models.RagRetrieveResponse
	if err := doJSONWithRetry(ctx, http.MethodPost, pyRagURL()+"/rag/retrieve",
		map[string]any{"question": question}, &r,
		map[string]string{"X-Admin-Token": ragAdminToken()}); err != nil {
		return r, fmt.Errorf("retrieve contexts: %w", err)
	}
	log.Printf("[RAG] retrieved %d contexts, confidence=%.4f, best_similarity=%.4f, has_embeddings=%v",
		len(r.Contexts), r.Confidence, r.BestSimilarity, r.HasEmbeddings)
	return r, nil
}

// isOffTopic returns true when the retrieved result fails the two-layer relevance gate.
//
// Layer 1 — RRF confidence (keyword signal):
//
//	Pure-dense-only score (no BM25 term overlap) ≈ 1/60 = 0.0167.
//	Catches greetings and gibberish where BM25 finds nothing at all.
//
// Layer 2 — cosine similarity (semantic signal):
//
//	best_similarity is the raw cosine between the question embedding and
//	the single closest doc across the full corpus (unfiltered, n=1 search).
//	Unlike RRF, this measures actual meaning overlap, not retrieval agreement.
//	"meaning of life" → cosine ≈ 0.12 vs any C/git doc → blocked.
//	"what is malloc"  → cosine ≈ 0.80 vs malloc doc   → passes.
//	Threshold 0.55 sits between unrelated (~0.10–0.30) and on-topic (~0.65–0.90).
//	Tune by watching logs: docker compose logs llm-server -f
func isOffTopic(r models.RagRetrieveResponse) bool {
	if r.Confidence < minRagConfidence {
		return true
	}
	// Semantic gate: only applied when NumpyIndex was built at startup.
	// When has_embeddings=false (embedding service was down), best_similarity
	// is always 0.0 — applying the gate would block all queries. Fall back to
	// the RRF confidence gate alone, which still requires actual keyword overlap.
	if r.HasEmbeddings && r.BestSimilarity < minCosineSimilarity {
		return true
	}
	return false
}

// isDirectBypass returns true when the best-matching doc is close enough to skip Ollama.
// Tier 1: high-similarity match — return stored answer verbatim.
// Gemma3:4b truncates long answers even at temp 0.3; bypassing the LLM for
// near-identical questions guarantees the full seed answer is returned.
func isDirectBypass(r models.RagRetrieveResponse) bool {
	return r.HasEmbeddings && r.BestSimilarity >= directBypassSimilarity && len(r.Contexts) > 0
}

// buildContextString extracts answer-only text from each context hit and joins them.
// extractAnswer strips the "Q: ..." prefix (retrieval metadata, redundant for the LLM).
func buildContextString(contexts []models.RagRetrieveContext) string {
	if len(contexts) == 0 {
		return "(no context retrieved)"
	}
	blocks := make([]string, len(contexts))
	for i, c := range contexts {
		extracted := extractAnswer(c.Text)
		log.Printf("[RAG] context[%d] raw_len=%d extracted_len=%d", i+1, len(c.Text), len(extracted))
		blocks[i] = fmt.Sprintf("[%d] %s", i+1, extracted)
	}
	return strings.Join(blocks, "\n\n")
}

// streamOllama sends the prompt to Ollama and returns a channel of streamed tokens.
// A background goroutine accumulates the full answer and caches it on clean completion.
func streamOllama(ctx context.Context, question, prompt string) (<-chan string, error) {
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
	go ForwardAndAccumulate(ctx, rawCh, outCh, func(answer string) {
		log.Printf("[RAG] ollama final answer len=%d: %q", len(answer), answer)
		if answer == "" {
			select {
			case outCh <- models.StreamErrSentinel + "empty model answer":
			case <-ctx.Done():
			}
			return
		}
		// Cache all answers including model refusals — repeated off-topic queries
		// should hit the cache (fast path) instead of triggering a new Ollama call.
		ragCacheSet(question, answer)
	})
	return outCh, nil
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
		return staticChan(cached), nil
	}
	log.Printf("[RAG] cache MISS for %q — calling python-rag", question)

	retrieved, err := fetchRAGContexts(ctx, question)
	if err != nil {
		return nil, err
	}
	if isOffTopic(retrieved) {
		return staticChan("Hi! I can only help with 42 curriculum projects. Shoot :)"), nil
	}
	if isDirectBypass(retrieved) {
		// Python pins the topic intro doc at Contexts[0] with rrf_score=0.0 regardless
		// of whether it is the best-matching doc.  The actual best match has the highest
		// RRFScore, so we pick that instead of always taking the intro at index 0.
		best := retrieved.Contexts[0]
		for _, c := range retrieved.Contexts[1:] {
			if c.RRFScore > best.RRFScore {
				best = c
			}
		}
		answer := "From community: " + extractAnswer(best.Text)
		log.Printf("[RAG] direct answer (similarity=%.4f) — skipping Ollama", retrieved.BestSimilarity)
		ragCacheSet(question, answer)
		return staticChan(answer), nil
	}

	prompt := buildRAGPrompt(buildContextString(retrieved.Contexts), question)
	log.Printf("[RAG] prompt total_len=%d, sending to ollama model=%s", len(prompt), chatModelName())
	return streamOllama(ctx, question, prompt)
}
