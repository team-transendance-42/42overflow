Step 1 — install Ollama
curl -fsSL https://ollama.com/install.sh | sh

That is the official Linux install command.

Step 2 — verify install
ollama -v

The docs use ollama -v to verify it is installed and running.

Step 3 — start the local server
ollama serve

Ollama serves its local API automatically when running. The API base URL is http://localhost:11434/api.

Open a second terminal after that.

Step 4 — download a model
ollama pull gemma4

ollama pull is the official command for downloading a model.

You can replace gemma4 with another model name later.

Step 5 — run it interactively
ollama run gemma4

That is the documented pattern.

Now type prompts directly.

Step 6 — list installed models
ollama ls

Official CLI command.

Step 7 — stop a loaded model
ollama stop gemma4

Official CLI command.

Step 8 — remove a model
ollama rm gemma4

Official CLI command.
=============================

call Ollama from curl
Simple generate request
curl http://localhost:11434/api/generate -d '{
  "model": "gemma4",
  "prompt": "Explain pointers like I am a beginner."
}'

This follows Ollama’s documented local API pattern.

Chat request
curl http://localhost:11434/api/chat -d '{
  "model": "gemma4",
  "messages": [
    { "role": "user", "content": "Explain epoll simply." }
  ]
}'

That matches the official /api/chat endpoint structure.

Part 6: call Ollama from Go

For your Go projects, this is the important part.

Minimal Go example
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Model    string        `json:"model"`
	Messages []ChatMessage `json:"messages"`
	Stream   bool          `json:"stream"`
}

type ChatResponse struct {
	Message struct {
		Role    string `json:"role"`
		Content string `json:"content"`
	} `json:"message"`
}

func main() {
	reqBody := ChatRequest{
		Model: "gemma4",
		Messages: []ChatMessage{
			{Role: "user", Content: "Explain goroutines simply."},
		},
		Stream: false,
	}

	data, err := json.Marshal(reqBody)
	if err != nil {
		panic(err)
	}

	resp, err := http.Post("http://localhost:11434/api/chat", "application/json", bytes.NewBuffer(data))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}

	if resp.StatusCode != http.StatusOK {
		fmt.Println("error:", string(body))
		return
	}

	var out ChatResponse
	if err := json.Unmarshal(body, &out); err != nil {
		panic(err)
	}

	fmt.Println(out.Message.Content)
}
====================================

On Linux, Ollama documents a systemd service setup:

create an ollama user
create /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

That is useful if you want your local LLM server always ready after boot.
----

create your own custom model behavior

Ollama uses a Modelfile. The docs describe it as the blueprint for a customized model, with instructions like FROM, PARAMETER, SYSTEM, TEMPLATE, and ADAPTER.

Example:

Modelfile

FROM gemma4
SYSTEM """You are a careful programming tutor. 
Explain simply, step by step, with short examples."""
PARAMETER temperature 0.2

Then create it:

ollama create mytutor -f Modelfile

Run it:

ollama run mytutor

The CLI docs show ollama create -f Modelfile as the custom-model pattern.
