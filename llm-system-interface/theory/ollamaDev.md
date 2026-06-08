On Linux:
* 1
curl -fsSL https://ollama.com/install.sh | sh

ollama serve

// ollama is like a runtime environment or manager for LLM models. (similar to how Docker runs containers, or how Python runs scripts)
qwen3:8b = the actual LLM model (the application/software)

* 2
New terminal: (less smart model: however, the only one i could find to be able to run on my machine)

ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b

Best picks in Ollama right now: april 2026

General talk: ollama pull qwen2.5:14b // too heavy for most laptops, can try for powerful remote server, best 32/72b models: qwen2.5:32b or qwen2.5:72b
Coding: qwen2.5-coder:32b // too heavy for my laptop


* 3
Then test API:

curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [
    { "role": "user", "content": "Explain channels in Go simply." }
  ]
}'

* 4
After that, connect your Go backend to http://localhost:11434/api/chat. // default Ollama chat API endpoint
===========================

Your request to Ollama should go to:

POST http://localhost:11434/api/chat

{
  "model": "codellama",
  "messages": [
    { "role": "user", "content": "your prompt here" }
  ],
  "stream": false
}

=========================
Start Ollama:

ollama serve

Pull model:

ollama pull codellama

Run your Go server:

go run .

Test:

curl -X POST http://localhost:8081/api/ai-assist \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain goroutines simply"}'
  ==============

  If qwen3:8b is too heavy

Try:

ollama pull qwen3:4b

Then in code change:

Model: "qwen3:4b",

7. If you want strongest coding quality instead of speed

Use:

ollama pull codellama:13b

Then:

Model: "codellama:13b",
=============================
codam: workaround for not sudo:
mkdir -p "$HOME/.local/ollama"
curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst \
  | tar --zstd -x -C "$HOME/.local/ollama"

export PATH="$HOME/.local/ollama/usr/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/.local/ollama/usr/lib/ollama:$LD_LIBRARY_PATH"
export OLLAMA_MODELS="$HOME/.local/share/ollama"
mkdir -p "$OLLAMA_MODELS"

ollama serve



























