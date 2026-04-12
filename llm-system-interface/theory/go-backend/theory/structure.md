llm-system/
├── main.go
├── handlers/
│   ├── text.go
│   └── image.go
├── middleware/
│   ├── ratelimit.go
│   └── errors.go
├── services/
│   ├── llm.go
│   └── imagegen.go
└── models/
    └── request.go

    ### package main

import (
    "log"                 // log server status and errors
    "net/http"            // HTTP server and request handling
    "github.com/gorilla/mux" // advanced HTTP routing
    "llm-system/handlers"     // request handler functions (e.g., GenerateText)
    "llm-system/middleware"   // middleware (rate limiting, error recovery)
)

func main() {
    r := mux.NewRouter() // Create a new router for handling HTTP requests using gori(third party package); Returns a *mux.Router object, which will handle HTTP routing (mapping URLs to handlers). Under the hood: Sets up internal data structures to match incoming HTTP requests to registered routes.

    // Apply middleware globally; Middleware is a function that wraps HTTP handlers to add extra behavior (like error handling).Under the hood: Each request passes through this middleware before reaching the handler.
    r.Use(middleware.ErrorRecovery)
    r.Use(middleware.RateLimiter) //Checks request rate and may block requests if limits are exceeded.

    r.HandleFunc("/generate", handlers.GenerateText).Methods("POST") //Registers the /generate route for POST requests, handled by GenerateText.
    r.HandleFunc("/generate-image", handlers.GenerateImage).Methods("POST")

    log.Println("Server running on :8080") //Built-in log package. Logs a message to the console 
    log.Fatal(http.ListenAndServe(":8080", r)) //Built-in net/http package. If the server fails to start, log.Fatal prints the error and exits.
Under the hood: Listens for incoming TCP connections, parses HTTP requests, and dispatches them to the router, which then calls the appropriate handler.
}

----------------

Request model + parser (models/request.go)

### package models

type TextRequest struct {
    Prompt string `json:"prompt"`
    Model  string `json:"model"`  // e.g. "gpt-4o", "claude-3"
    Stream bool   `json:"stream"`
}

type ImageRequest struct {
    Prompt string `json:"prompt"`
    Size   string `json:"size"`   // e.g. "1024x1024"
}

-----------------

Streaming text handler (handlers/text.go)

Call the LLM API with streaming enabled
Read SSE chunks (data: {...}\n\n)
Forward each chunk to the client via http.Flusher

### package handlers

import (
    "bufio"
    "encoding/json"
    "fmt"
    "net/http"
    "llm-system/models"
    "llm-system/services"
)

func GenerateText(w http.ResponseWriter, r *http.Request) {
    var req models.TextRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid request", http.StatusBadRequest)
        return
    }

    // Set SSE headers for streaming
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")

    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "streaming unsupported", http.StatusInternalServerError)
        return
    }

    // Stream tokens from service
    ch, err := services.StreamLLM(r.Context(), req)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadGateway)
        return
    }

    for chunk := range ch {
        fmt.Fprintf(w, "data: %s\n\n", chunk)
        flusher.Flush() // Send to client immediately — key for streaming UX
    }
}

