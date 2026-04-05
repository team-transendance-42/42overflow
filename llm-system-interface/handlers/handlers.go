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
	w.Header().Set("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
	// w.Header().Set("Access-Control-Allow-Origin", "*")
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

	log.Printf("GenerateText: received prompt len=%d", len(req.Prompt)) // debug, remove later
	req.Prompt = strings.TrimSpace(req.Prompt)
	if req.Prompt == "" {
		http.Error(w, "prompt is required", http.StatusBadRequest)
		return false
	}
	if len(req.Prompt) > 20000 {
		http.Error(w, "prompt too large", http.StatusRequestEntityTooLarge)
		return false
	}
	return true
}

/**
context.Context is an object that carries:
cancellation signal, timeout / deadline, request-scoped values
In web servers, every incoming HTTP request has its own context.
*/
func GenerateText(w http.ResponseWriter, r *http.Request) {
	log.Printf("GenerateText hit: method=%s path=%s", r.Method, r.URL.Path)
	if !setHeaders(w, r) { return }

	var req models.TextRequest
	if !validateTextReq(w, r, &req) { return }
	ch, err := services.StreamLLM(r.Context(), req)
	if err != nil {
		log.Printf("GenerateText: StreamLLM error: %v", err)
		http.Error(w, "LLM Service Error: "+err.Error(), http.StatusBadGateway)
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