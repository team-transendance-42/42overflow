package main
// go run main.go
import (
    "bufio"
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "strings"
    "sync"
    "time"
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

// Wait blocks until a token is available
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

// ── SSE stream ───────────────────────────────────────────
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
func Stream(apiKey, prompt string, out chan<- string)  {
    defer close(out)

    body, _ := json.Marshal(map[string]any{
        "model":      "claude-opus-4-5",
        "max_tokens": 1024,
        "stream":     true,
        "messages":   []map[string]string{{"role": "user", "content": prompt}},
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

        var ev Event
        if json.Unmarshal([]byte(payload), &ev) != nil { continue }
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