Concept explanations:

- http.Flusher: Used in the text handler to push SSE (Server-Sent Events) chunks to the client immediately, without buffering.
- goroutine + channel: Used in services/llm.go to enable non-blocking stream reading from upstream services.
- context.Context: Passed to all services so that if the client disconnects, upstream requests are cancelled automatically.
- sync.Mutex: Used in the rate limiter to ensure thread-safe access to the limiter map.
- bufio.Scanner: Used in the llm service to parse SSE responses line by line.
- defer recover(): Used in error middleware to recover from panics and return a proper HTTP 500 error response.

Concept	Where/Why
http.Flusher	In text handler; pushes SSE chunks to client without buffering
goroutine + channel	In services/llm.go; enables non-blocking stream reading
context.Context	Used in all services; cancels upstream requests if client disconnects
sync.Mutex	In rate limiter; ensures thread-safe access to limiter map
bufio.Scanner	In llm service; parses SSE line-by-line
defer recover()	In error middleware; recovers from panics and returns error as HTTP 500
-----------------------------
Steps:
router running and return a static "hello" from /generate
Add request parsing and return the prompt back as echo
Integrate one real LLM API call (non-streaming first)
Add streaming with http.Flusher
Add rate limiting middleware
Add error recovery and proper HTTP status codes
Add image generation as a second route