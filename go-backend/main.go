package main
// go run main.go
import (
    "bufio"      // for reading response body line by line (Scanner)
    "bytes"      // for converting JSON to a byte buffer for HTTP requests
    "encoding/json" // for marshaling/unmarshaling JSON data
    "fmt"        // for formatted I/O (e.g., Println)
    "net/http"   // for making HTTP requests
    "strings"    // for string manipulation (e.g., HasPrefix)
    "sync"       // for Mutex (used in rate limiter)
    "time"       // for time-related functions (e.g., Sleep, Now)
)

// ── Rate limiter ─────────────────────────────────────────
/**
Purpose: Prevents sending too many requests to the API in a short time (e.g., 50 requests per minute).
How: It keeps track of request timestamps. If you exceed the limit, it waits until a slot is free.
*/
type TokenBucket struct {
    mu         sync.Mutex
    timestamps []time.Time  // ring of recent call times
    limit      int          // max calls per window
    window     time.Duration
}

func NewBucket(limit int, window time.Duration) *TokenBucket {
    return &TokenBucket{limit: limit, window: window}
}

// Wait blocks until a token is available, (receive type) comes b4 func name: () before the name = method (has a receiver, like a class method in C++/Java)
// () after the name = function parameters (always required for both functions and methods)
func (b *TokenBucket) Wait() {
    for {
        b.mu.Lock()
        now := time.Now()
        cutoff := now.Add(-b.window)

        // drop timestamps outside the window
        i := 0
        for i < len(b.timestamps) && b.timestamps[i].Before(cutoff) {
            i++
        }
        b.timestamps = b.timestamps[i:]

        if len(b.timestamps) < b.limit {
            b.timestamps = append(b.timestamps, now)
            b.mu.Unlock()
            return   // token granted
        }

        // sleep until oldest timestamp expires
        sleep := b.timestamps[0].Add(b.window).Sub(now)
        b.mu.Unlock()
        time.Sleep(sleep)
    }
}

// ── SSE stream (server sent events) ────────────────────────────────────────────
type Delta struct {
    Type string `json:"type"`
    Text string `json:"text"`
}
type Event struct {
    Type  string `json:"type"`
    Delta Delta  `json:"delta"`
}

// Stream sends a prompt and writes tokens to out channel.
// Caller closes nothing — Stream closes out when done.
/**
chan<- string: A channel that receives strings (tokens) from the Stream function. The Stream function will send tokens to this channel as it receives them from the API. The caller can read from this channel to get the generated text in real-time.
In Go, a channel is a built-in type used for communication between goroutines (lightweight threads). You can think of it as a thread-safe queue or pipe:

It lets one goroutine send a value and another receive it, synchronizing them.
Channels are typed (e.g., chan string for strings).
Sending: ch <- value
Receiving: value := <-ch
In C/C++, you might use mutexes, condition variables, or message queues for similar inter-thread communication, but Go channels are simpler and built into the language for safe, concurrent programming.

Go does not have C++-style references (aliases), only pointers. All function arguments in Go are passed by value, but you can pass a pointer to allow the function to modify the original value. In this case, the channel is passed by value (the channel itself is a reference type), so the Stream function can send tokens to the channel, and the caller can read from it without needing to pass a pointer to the channel.

*/
/**
sends a prompt to the API and receives a streaming response.
s it receives each chunk of text (token), it sends that token to the out channel (out <- ...).
When done, it closes the out channel (defer close(out)).

stream data from the API and push each piece to the channel, so other parts of your program (like main) can read and process the tokens as they arrive.
*/
func Stream(apiKey, prompt string, out chan<- string)  {
    defer close(out) //  It ensures the channel out is closed when the Stream function ends, even if there’s an error or early return.

	// body, _ multiple return values, we ignore the error here for brevity, but in production code, you should handle it properly.
	/* serialize go val into json format */
    body, _ := json.Marshal(map[string]any{
        "model":      "claude-opus-4-5",
        "max_tokens": 1024,
        "stream":     true,
        "messages":   []map[string]string{{"role": "user", "content": prompt}}, //  list (slice) of message objects, each represented as a map with keys "role" and "content". It matches the expected format for many chat/LLM APIs, where you send a list of messages (each with a role and content).    []map[string]string in Go is similar to an array of objects (2D map) in Js, where each object has string keys and values. 
    })

    req, _ := http.NewRequest("POST", "https://api.anthropic.com/v1/messages", bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("x-api-key", apiKey)
    req.Header.Set("anthropic-version", "2023-06-01")

    resp, err := http.DefaultClient.Do(req)
    if err != nil { return }
    defer resp.Body.Close()

    scanner := bufio.NewScanner(resp.Body)
    for scanner.Scan() {
        line := scanner.Text()
        if !strings.HasPrefix(line, "data: ") { continue }
        payload := line[6:]
        if payload == "[DONE]" { break }

        var ev Event // var ev of type Event (struct defined above)
        if json.Unmarshal([]byte(payload), &ev) != nil { continue } // []byte(built in type conversion)convert json to bytes, then unmarshal into ev struct, if error, skip
        if ev.Type == "content_block_delta" && ev.Delta.Type == "text_delta" {
            out <- ev.Delta.Text  // push token to channel

        }
    }
}

// ── Main ─────────────────────────────────────────────────
func main() {
    bucket := NewBucket(50, 60*time.Second)  // 50 req/min
    out := make(chan string, 64)

    bucket.Wait()  // blocks if rate limit exceeded
    go Stream("sk-ant-...", "Hello, Claude!", out)

    for token := range out {
        fmt.Print(token)  // or push to your UI
    }
    fmt.Println()
}


// package main

// import "fmt"

// func main() {
// 	fmt.Println("Hallo world")
// }