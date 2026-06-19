The LLM server is a Go HTTP proxy that sits between your frontend and the actual AI models. The frontend never talks to Gemini or Ollama
  directly.

  ---
  Step 1 — Request arrives from the frontend
  
  The frontend sends a POST with JSON like { "prompt": "what is a Makefile?" } to one of three routes:

  ┌────────────────┬────────────────────────────────────────────────────────────────────┐
  │     Route      │                              Purpose                               │
  ├────────────────┼────────────────────────────────────────────────────────────────────┤
  │ /api/ai-assist │ General chat — powered by Google Gemini                            │
  ├────────────────┼────────────────────────────────────────────────────────────────────┤
  │ /api/ollama    │ Raw Ollama chat — local model                                      │
  ├────────────────┼────────────────────────────────────────────────────────────────────┤
  │ /api/community │ RAG (community knowledge) — powered by Ollama + Python RAG service │
  └────────────────┴────────────────────────────────────────────────────────────────────┘
---
  Step 2 — Middleware runs on every request

  Before any handler executes, three middleware layers fire in order:

  1. ErrorRecovery — catches any Go panic so the server doesn't crash
  2. InternalSecret — rejects requests missing the X-Internal-Secret header (keeps the server private)
  3. RateLimiter — prevents abuse by capping how many requests a client can send

  ---
Step 3 — Request is validated and normalized

  The handler:
  - Decodes the JSON body
  - Trims whitespace from the prompt
  - If only { "prompt": "..." } was sent, wraps it into a proper messages array [{role: "user", content: "..."}] — because both Gemini and Ollama
  need the messages format
  - Rejects if total message content exceeds 20,000 characters
Step 3 — Request is validated and normalized

  The handler:
  - Decodes the JSON body
  - Trims whitespace from the prompt
  - If only { "prompt": "..." } was sent, wraps it into a proper messages array [{role: "user", content: "..."}] — because both Gemini and Ollama
  need the messages format
  - Rejects if total message content exceeds 20,000 characters
