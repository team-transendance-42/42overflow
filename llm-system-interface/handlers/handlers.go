package handlers

import (
	"encoding/json"
	"llm-system-interface/models"
	"llm-system-interface/services"
	"log"
	"net/http"
	"strings"
)

func setHeaders(w http.ResponseWriter, r *http.Request) bool {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return false
	}
	return true
}

func decodeAndSanitize(w http.ResponseWriter, r *http.Request, req *models.TextRequest) bool {
	if err := json.NewDecoder(r.Body).Decode(req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return false
	}
	req.Prompt = strings.TrimSpace(req.Prompt) // only begin and end
	return true
}

/*
compitability layer:
Frontend can send just { "prompt": "hello" } or full { "messages": [{...}] }.
Both Gemini and Ollama expect req.Messages to be populated — never just a raw prompt.
If messages is empty, wraps the prompt into a single user message so both models
receive one consistent format regardless of what the frontend sent.
*/
func normalizeMessages(w http.ResponseWriter, req *models.TextRequest) bool {
	if len(req.Messages) == 0 {
		if req.Prompt == "" {
			http.Error(w, "prompt or messages required", http.StatusBadRequest)
			return false
		}
		req.Messages = []models.Message{
			{Role: models.RoleUser, Content: req.Prompt},
		}
		req.Prompt = "" // prevent buildGeminiContentsFromRequest from appending it a second time
	}
	return true
}

func validateMessageSize(w http.ResponseWriter, req *models.TextRequest) bool {
	total := 0
	for _, m := range req.Messages {
		total += len(m.Content)
	}
	if total > 20000 {
		http.Error(w, "total message content too large, max 20000 chars", http.StatusRequestEntityTooLarge)
		return false
	}
	log.Printf("validateTextReq: %d messages, total_len=%d", len(req.Messages), total)
	return true
}

func validateTextReq(w http.ResponseWriter, r *http.Request, req *models.TextRequest) bool {
	return decodeAndSanitize(w, r, req) &&
		normalizeMessages(w, req) &&
		validateMessageSize(w, req)
}

/*
*
context.Context is an object that carries:
cancellation signal, timeout / deadline, request-scoped values
In web servers, every incoming HTTP request has its own context.

flusher is an object that implements the http.Flusher interface.
w.(http.Flusher) is a type assertion: it checks if w (the http.ResponseWriter) also supports the Flush() method (needed for streaming).
If ok is true, flusher is the same as w, but now can call flusher.Flush() which
forces Go’s HTTP server to immediately send any data written (with fmt.Fprintf, etc.) to the client, instead of waiting for the buffer to fill up.
chunk is a string received from the channel (ch), which may contain multiple lines separated by \n.
for _, line := range strings.Split(chunk, "\n") splits the chunk into individual lines, and each line is sent as a separate SSE message: fmt.Fprintf(w, "data: %s\n", line).
After all lines in the chunk are sent, fmt.Fprint(w, "\n") writes an extra newline. In SSE, a blank line (\n) signals the end of one event/message to the browser.
flusher.Flush() is called after writing all lines and the extra newline, forcing Go to send everything to the client immediately.
We want to send a complete SSE event (all lines + the blank line) as one unit, then flush. This ensures the browser receives a full, well-formed SSE message right away.
If we flushed before the final newline, the browser might see an incomplete event and not process it until the next flush.
The first flusher.Flush() (inside the loop) sends each streamed chunk to the client as soon as it’s ready, so the user sees updates in real time.

The second flusher.Flush() (after fmt.Fprintf(w, "event: end\ndata: \n\n")) is for the final SSE event that signals the end of the stream. It ensures that this last message is also sent immediately, not left in the buffer.

Even though there’s nothing more to send after that, it’s good practice to flush after the final event to guarantee the client receives the “end” signal right away, especially if there’s any data left in the buffer.
*/
/*
First flush: for each streamed chunk/event to be read by browser
Second flush: for the final “end” event, to guarantee delivery.
*/
func GenerateGeminiText(w http.ResponseWriter, r *http.Request) {
	log.Printf("GenerateGeminiText(): method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) {
		return
	}

	var req models.TextRequest
	if !validateTextReq(w, r, &req) {
		return
	}

	ch, err := services.StreamGemini(r.Context(), req)
	if err != nil {
		log.Printf("GenerateGeminiText: StreamGemini error: %v", err)
		http.Error(w, "LLM Service Error: "+err.Error(), http.StatusBadGateway)
		return
	}

	streamSSE(w, ch) // talks to browser, sending each chunk as an SSE message
}
