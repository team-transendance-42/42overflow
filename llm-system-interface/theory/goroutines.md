c := make(chan int)

go func() { c <- 3 }() // Create a new goroutine that puts 3 to the channel

fmt.Println(<-c) // Take 3 from the channel and print it in the main thread
------------------------

// unbuffered
messages := make(chan string)
go func() { messages <- "ping" }()
msg := <-messages

// buffered (capacity 1)
messages := make(chan string, 1)
func() { messages <- "ping" }()
msg := <-messages
===

Goroutine vs channel: core difference

Goroutine:
A lightweight concurrent execution unit. It is about running work in parallel/concurrently.

Channel:
A communication pipe between goroutines. It is about sending data and synchronization.
===

One worker reads Gemini SSE and produces text chunks
Another worker (HTTP handler) consumes chunks and writes SSE to browser
If both are not concurrent, producer blocks waiting for consumer.
So:

goroutine gives concurrency
channel gives safe handoff of chunks
Why one channel is enough here
One stream of data, one direction:
Gemini reader -> HTTP writer
===

Browser asks question
Handler calls StreamLLM
StreamLLM starts background producer goroutine
StreamLLM returns channel immediately
Handler starts reading channel and streaming to browser
Producer closes channel when Gemini stream ends
Handler loop exits and sends final end even