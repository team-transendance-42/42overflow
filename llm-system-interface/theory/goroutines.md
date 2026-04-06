In Go, a goroutine is a lightweight thread of execution managed by the Goruntime, rather than the operating system.

Think of a goroutine as a "function that runs independently and concurrently" alongside other functions.Here is a breakdown of what makes them special and how they work.

---

1. Key Characteristics
*Multiplexed: The Go runtime uses a technique called M:N scheduling. It maps M goroutines ontoN OS threads. If one goroutine blocks (e.g., waiting for I/O), the schedulermoves other goroutines to a different OS thread so work doesn't stop.

Lightweight: While an OS thread typically takes 1MB of stack space, a goroutine starts with a very small stack (usually 2KB). This allows you to run hundreds of thousands (or even millions) of goroutines on a single machine.
Easy to Start: You simplyput the keyword go in front of any function call.
---

2. How to use itTo run a function as a goroutine, add the go keyword:
package main

import ("fmt"
"time"
)sud

func sayHello() {
fmt.Println("Hello from Goroutine!")
}

func main() {
// Start the function as a goroutine
go sayHello()// Wait a bit to ensure the goroutine has time to finish
// (Otherwise, main might exit before the goroutine runs)
time.Sleep(1 * time.Second)
fmt.Println("Main function finished.")
}
3. The "Gotcha": Synchronization
Goroutines are asynchronous. If your main function finishes, the program exits immediately, killing all running goroutines.

In real-world applications, you don't usetime.Sleep to wait for goroutines. Instead, you use:

Channels: Forcommunication and synchronization between goroutines.
`sync.WaitGroup`: To wait for a collection of goroutines to completetheir work.
---

4. Comparison: Goroutines vs. OS Threads
| Feature | Goroutines| OS Threads | | :--- | :--- | :--- | | Memory | Very small (~2KB) | Large (~1MB+) | | Creation | Fast (User-space) | Slow (Kernel call) | | Context Switching | Fast (No kernel involvement) | Slow (Requires kernel mode) | |Management | Go Runtime | Operating System |

---

5. Best Practice: Communicating
Thereis a famous proverb in the Go community: > "Do not communicate by sharing memory; instead, share memory bycommunicating."

This means that instead of using shared variables (which requires complex locking/mutexes), you should use Channels to pass data between goroutines.

Summary
*Use channels to send data between tasks.

Use go to fire off a task.
Use sync package (like WaitGroup) if you need to coordinate thelifecycle of multiple goroutines.
Goroutines are the "secret sauce" that makes Go extremely efficient for network servers, microservices, and high-concurrency applications.

===
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