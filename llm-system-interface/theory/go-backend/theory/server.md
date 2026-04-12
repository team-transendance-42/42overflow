
You should NOT call the Anthropic API directly from your Svelte frontend. This would expose your secret API key to anyone using your site, which is a security risk.
server.go acts as a backend “middleman.” Your Svelte frontend sends the user's question to your Go server, which then safely calls the Anthropic API (with your secret key) and returns the answer.
This keeps your API key secure and lets you add rate limiting, logging, or other backend logic.


======================================
import standard Go packages for:

HTTP requests and responses
JSON encoding/decoding
String and time manipulation
Concurrency (sync, channels)
Buffered I/O
------------------------------
2. Rate Limiter (TokenBucket)
Purpose:
Prevents sending too many requests to the API in a short time (e.g., 50 requests per minute).

How:

Keeps a list of timestamps for recent requests.
When a new request is about to be made, it checks if the number of requests in the last window (e.g., 60 seconds) exceeds the limit.
If yes, it waits until a slot is free (oldest timestamp expires).
This is a classic “token bucket” algorithm for rate limiting.
Key methods:

NewBucket(limit, window): creates a new rate limiter.
Wait(): blocks until a request can be made without exceeding the rate limit.
-------------------------------
3. Data Structures for Streaming
Delta: Represents a chunk of streamed text from the API (with type and text).
Event: Represents a full event from the API, which contains a Delta.
--------------------------------
4. Stream Function
Signature:
func Stream(apiKey, prompt string, out chan<- string)

Purpose:
Sends a prompt to the LLM API and streams the response tokens (words/chunks) as they arrive, sending each token to the out channel.

How:

Builds a JSON request body with the prompt and model info.
Creates an HTTP POST request to the API endpoint, sets headers (API key, content type, version).
Sends the request and gets a streaming response (SSE).
Reads the response line by line.
For each line starting with "data: ", strips the prefix and checks for "[DONE]" (end of stream).
Unmarshals the JSON payload into an Event struct.
If the event is a text delta, sends the text to the out channel.
Closes the out channel when done.
Theory:
This function is a producer in a producer-consumer pattern, using a Go channel to send data to another goroutine.
--------------------------------
5. Main Function
Purpose:
Coordinates the rate limiter and streaming, and prints the streamed tokens.

How:

Creates a rate limiter (50 requests per 60 seconds).
Creates a channel for streaming tokens.
Waits for a token (rate limit).
Starts the Stream function in a new goroutine (so it runs concurrently).
Reads tokens from the out channel as they arrive and prints them.
Prints a newline at the end.
Theory:

Uses Go's concurrency model (goroutines and channels) to handle streaming data and rate limiting efficiently.
The main function is the consumer, reading from the channel and displaying the output.
--------------------------------
6. Summary
What does the whole file do?

It implements a command-line tool that sends a prompt to an LLM API (like Claude), respects API rate limits, and prints the streamed response in real time as it arrives.
It uses Go's concurrency primitives (goroutines, channels, mutexes) for safe, efficient, and real-time communication between different parts of the program.
Why is this design good?

It's scalable: you can handle many requests and responses efficiently.
It's safe: rate limiting prevents API abuse.
It's responsive: streaming lets you show results as soon as they're available, not waiting for the whole response.
-----------------------------------
The go keyword before Stream launches the Stream function as a goroutine—a lightweight, concurrent thread managed by Go.

So, go Stream("sk-ant-...", "Hello, Claude!", out) means:

Start the Stream function in the background (concurrently).
The main function continues running without waiting for Stream to finish.
Stream will send tokens to the out channel as they arrive, while main can read from that channel at the same time.
This is Go’s way of doing concurrency, allowing your program to handle streaming and output simultaneously.
--------------------------------
Using the LLM (like Claude) directly from its website is fine for manual, individual use. However, this Go code is needed when you want to:

Integrate the LLM into your own app, website, or workflow (e.g., your Svelte frontend).
Automate sending prompts and processing responses (not just typing in a web UI).
Stream responses in real time to your users or systems.
Enforce rate limits to avoid hitting API usage caps or bans.
Build custom features (e.g., logging, analytics, chaining with other APIs, or advanced UI).
Use the LLM as a backend service for multiple users or automated tasks.
In summary:
The code lets you programmatically access, control, and extend the LLM’s capabilities—something you can’t do just by using the website.