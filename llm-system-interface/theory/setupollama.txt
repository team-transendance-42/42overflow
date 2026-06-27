Then on the machine running Ollama:

ollama pull llama3.2        # ~2GB download
ollama serve                # starts on :11434

# switch your Go server to it:
PROVIDER=ollama go run llm_server.go