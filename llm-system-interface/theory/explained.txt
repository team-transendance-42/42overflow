Concept explanations:

- http.Flusher: Used in the text handler to push SSE (Server-Sent Events) chunks to the client immediately, without buffering.
- goroutine + channel: enable non-blocking stream reading from upstream services.
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
==================================
goroutines, channels
==================================
Goroutine:
A goroutine is a lightweight thread managed by Go. You can start thousands of them with very little memory. They run functions “in the background” so your program can do many things at once.
Channel:
A channel is a safe way for goroutines to send data to each other. Think of it as a pipe: one goroutine puts data in, another takes it out. Channels make it easy to communicate and synchronize between goroutines.

When you call go myFunc(), Go creates a new goroutine (like a thread, but much lighter).
Channels are built into Go’s runtime. They use locks and queues to safely pass data between goroutines, avoiding race conditions.

In C, you use pthreads for threads and OS pipes for communication. Threads are heavy (lots of memory), and pipes are for bytes, not typed data.
In Go, goroutines are much lighter than OS threads, and channels are typed and safe (no manual locking needed).
---
Why use goroutines?

To handle many tasks at once (like reading from a network, waiting for an LLM response, or streaming data) without blocking the main program.
For streaming: one goroutine reads from the LLM API, sends each chunk through a channel; the main handler reads from the channel and streams to the client.
---

How many goroutines?

Usually, one per concurrent task. For streaming, you might have:
1 main handler goroutine (serving the HTTP request)
1 goroutine reading from the LLM API and sending data to the channel
---

Channel = connection?

Yes! The channel is the “pipe” between the main handler and the goroutine. The main handler reads from the channel as data arrives, so it can stream to the client without blocking.
Summary:

Goroutines = lightweight threads (much cheaper than C threads)
Channels = safe, typed pipes for communication between goroutines
You use them to do non-blocking, concurrent work (like streaming) easily and safely in Go.



