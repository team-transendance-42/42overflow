Go to aistudio.google.com → sign in with Google
Click "Get API Key" → Create API key in new project
Copy the AIza... key and set it as an environment variable:
export GEMINI_API_KEY="AIza..."

run:
# With Gemini (free, no card)
export PROVIDER=gemini
export GEMINI_API_KEY=AIzaxxxxx
go run llm_server.go

# Test it
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello!"}]}'


