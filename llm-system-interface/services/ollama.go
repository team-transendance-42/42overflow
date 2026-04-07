package services

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
    "os"
)

// Ollama request/response structs
type OllamaMessage struct {
    Role    string `json:"role"`
    Content string `json:"content"`
}

type OllamaRequest struct {
    Model    string          `json:"model"`
    Messages []OllamaMessage `json:"messages"`
    Stream   bool            `json:"stream"`
}

type OllamaResponse struct {
    Message OllamaMessage `json:"message"`
    Done    bool          `json:"done"`
}

/* StreamOllama sends a prompt to Ollama and returns chunks via channel */
func StreamOllama(ctx context.Context, prompt string) (<-chan string, error) {
    ch := make(chan string)
	const conciseInstruction = "Be my tutor: use less words,dry";

    model := os.Getenv("OLLAMA_MODEL")
    if model == "" {
        model = "codellama"
    }
    
    ollamaURL := os.Getenv("OLLAMA_URL")
    if ollamaURL == "" {
        ollamaURL = "http://localhost:11434"
    }
    
    reqBody := OllamaRequest{
        Model: model,
        Messages: []OllamaMessage{
            {Role: "user", Content: conciseInstruction + "." + prompt},
        },
        Stream: true,
    }
    
    body, err := json.Marshal(reqBody)
    if err != nil {
        return nil, err
    }
    
    // Make HTTP request to Ollama with configurable URL
    req, err := http.NewRequestWithContext(ctx, "POST", ollamaURL+"/api/chat", bytes.NewReader(body))
    if err != nil {
        return nil, err
    }
    req.Header.Set("Content-Type", "application/json")
    
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("Ollama request failed: %w", err)
    }
    
    if resp.StatusCode != http.StatusOK {
        defer resp.Body.Close()
        respBody, _ := io.ReadAll(resp.Body)
        return nil, fmt.Errorf("Ollama HTTP %d: %s", resp.StatusCode, string(respBody))
    }
    
    // Stream response in background
    go func() {
        defer close(ch)
        defer resp.Body.Close()
        
        decoder := json.NewDecoder(resp.Body)
        for {
            var ollamaResp OllamaResponse
            if err := decoder.Decode(&ollamaResp); err != nil {
                if err != io.EOF {
                    log.Printf("Ollama decode error: %v", err)
                }
                break
            }
            
            if ollamaResp.Message.Content != "" {
                ch <- ollamaResp.Message.Content
            }
            
            if ollamaResp.Done {
                break
            }
        }
    }()
    
    return ch, nil
}
