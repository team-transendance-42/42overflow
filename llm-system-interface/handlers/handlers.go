package handlers

import (
	// "bufio" for waht?
	"encoding/json"
	"fmt"
	"llm-system-interface/models"
	"llm-system-interface/services"
	"net/http"
	"strings"
	"log"
)

/**
for chunk := range ch {
for range loop specifically designed for channels. It will continue to pull data from the channel ch until the channel is closed
---
fmt.Fprintf(w, "data: %s\n\n", chunk)

Syntax: fmt.Fprintf writes a formatted string to an io.Writer. In this case, the http.ResponseWriter (w) acts as that writer.
Theory: SSE is a text-based protocol. To be valid, the browser expects a specific format: the word data:, followed by the message, followed by two newline characters (\n\n).
Under the Hood: * w usually points to a buffer. Without the next line, the operating system or Go's standard library might hold onto this data to send it in one large "clump" later to improve network efficiency.
The \n\n is critical; it tells the client's EventSource API that one complete message has finished.
---
flusher.Flush()

Syntax: This calls the Flush method on an object that implements the http.Flusher interface.
Theory: Standard HTTP is "request-response"—the server sends the whole body at once. SSE is "streaming." If you don't flush, the user might wait seconds or minutes to see any data because the server is waiting for its internal buffer (usually 4KB or 8KB) to fill up.
Under the Hood: * This sends a signal to the underlying TCP socket to "push everything we have in the buffer right now."
It bypasses the standard buffering logic of the Go web server.
This allows for the "typing" effect or real-time ticker updates, as the browser receives the bytes immediately after they are written.
*/

func setHeaders(w http.ResponseWriter, r *http.Request) bool {
	w.Header().Set("Access-Control-Allow-Origin", "http://127.0.0.1:5173") // todo: vite dev server, in prod: need to update to match the real frontend URL
	// w.Header().Set("Access-Control-Allow-Origin", "*") // only for testing: 
	w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusNoContent)
		return false
	}
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return false
	}
	return true
}

func validateTextReq(w http.ResponseWriter, r *http.Request, req *models.TextRequest) bool {
	if err := json.NewDecoder(r.Body).Decode(req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return false
	}

	log.Printf("GenerateText: received prompt len=%d", len(req.Prompt))
	req.Prompt = strings.TrimSpace(req.Prompt)
	if req.Prompt == "" {
		http.Error(w, "prompt is required", http.StatusBadRequest)
		return false
	}
	if len(req.Prompt) > 20000 {
		http.Error(w, "prompt too large, max allowed len 20000", http.StatusRequestEntityTooLarge)
		return false
	}
	return true
}

/**
context.Context is an object that carries:
cancellation signal, timeout / deadline, request-scoped values
In web servers, every incoming HTTP request has its own context.

flusher is an object that implements the http.Flusher interface.
w.(http.Flusher) is a type assertion: it checks if w (the http.ResponseWriter) also supports the Flush() method (needed for streaming).
If ok is true, flusher is the same as w, but now you can call flusher.Flush() which
forces Go’s HTTP server to immediately send any data written (with fmt.Fprintf, etc.) to the client, instead of waiting for the buffer to fill up.
chunk is a string received from the channel (ch), which may contain multiple lines separated by \n.
for _, line := range strings.Split(chunk, "\n") splits the chunk into individual lines, and each line is sent as a separate SSE message: fmt.Fprintf(w, "data: %s\n", line).
After all lines in the chunk are sent, fmt.Fprint(w, "\n") writes an extra newline. In SSE, a blank line (\n) signals the end of one event/message to the browser.
flusher.Flush() is called after writing all lines and the extra newline, forcing Go to send everything to the client immediately.
You want to send a complete SSE event (all lines + the blank line) as one unit, then flush. This ensures the browser receives a full, well-formed SSE message right away.
If you flushed before the final newline, the browser might see an incomplete event and not process it until the next flush.
The first flusher.Flush() (inside the loop) sends each streamed chunk to the client as soon as it’s ready, so the user sees updates in real time.

The second flusher.Flush() (after fmt.Fprintf(w, "event: end\ndata: \n\n")) is for the final SSE event that signals the end of the stream. It ensures that this last message is also sent immediately, not left in the buffer.

Even though there’s nothing more to send after that, it’s good practice to flush after the final event to guarantee the client receives the “end” signal right away, especially if there’s any data left in the buffer.

Summary:

First flush: for each streamed chunk/event.
Second flush: for the final “end” event, to guarantee delivery.
*/
func GenerateText(w http.ResponseWriter, r *http.Request) {
	log.Printf("GenerateText(): method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) { return }

	var req models.TextRequest
	if !validateTextReq(w, r, &req) { return }
	ch, err := services.StreamLLM(r.Context(), req)
	if err != nil {
		log.Printf("GenerateText: StreamLLM error: %v", err)
		http.Error(w, "LLM Service Error: "+err.Error(), http.StatusBadGateway) // writes to client
		return
	}

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming not supported", http.StatusInternalServerError)
		return
	}

	for chunk := range ch {
		for _, line := range strings.Split(chunk, "\n") {
			fmt.Fprintf(w, "data: %s\n", line)
		}
		fmt.Fprint(w, "\n")
		flusher.Flush()
	}

	fmt.Fprintf(w, "event: end\ndata: \n\n")
	flusher.Flush()
}

/**Images don't stream — they return a JSON response with a URL or base64 bytes.*/
func GenerateImage(w http.ResponseWriter, r *http.Request) {
	var req models.ImageRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	// imageURL, err := services.GenerateImage(r.Context(), req)
	// if err != nil {
	// 	http.Error(w, err.Error(), http.StatusBadGateway)
	// 	return
	// }

	// w.Header().Set("Content-Type", "application/json")
	// json.NewEncoder(w).Encode(map[string]string{"url": imageURL})
}