ep 1:
HTTP Client Sends a POST request to /generate (Text) or /generate-image (Image).
===
Step 2:
main.go — HTTP Router net/http + gorilla/mux intercepts the request and matches it to the defined route handlers.
===
Step 3: Global Middleware Chain
3.1 Rate Limiter: (Token Bucket / Sliding Window) Checks user headers or IP against a store (like Redis) to allow or block (429) the request.

3.2 Request Parser: (json.Decoder) Extracts the raw JSON body into a Go struct.

3.3 Error Handler: A deferred recovery and logging middleware that ensures any downstream panic results in a clean JSON error response.
===
Step 4: Service Logic (The Branch)
Route A: LLM Text Service (/generate) * Integration: Initiates an SSE (Server-Sent Events) request to Gemini(or chosen LLM).

Action: The Stream Writer uses http.Flusher to push chunks to the client in real-time.

Output: text/event-stream (Type: Chunked SSE → client flush).

Route B: Image Gen Service (/generate-image) * Integration: Calls DALL·E or Stability API via standard http.Post.

Action: The JSON Response Writer waits for the full binary data or URL to return.

Output: application/json (Type: image_url or base64 bytes).
===

Step 5: Final Response Delivery
Text: The connection closes after the final "done" signal is sent via SSE.

Image: The HTTP body is written once with the full payload and the connection terminates.


