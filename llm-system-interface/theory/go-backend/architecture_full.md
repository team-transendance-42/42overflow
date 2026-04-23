======================
Entry Point
llm_server.go
=====================
Loads .env, sets up gorilla/mux router
Registers 4 routes → maps each to a handler
Wires middleware chain: ErrorRecovery → RateLimiter → handler
Starts background cleanup goroutine via middleware.StartCleanup()

=====================================
Middleware (runs on every request)
=====================================
middleware/errors.go
---------------------
ErrorRecovery — wraps next handler in a recover() defer, catches panics, returns 500

middleware/ratelimiter.go
-------------------------
RateLimiter — two-tier token bucket
Global: 10 req/min burst 5 (protects Gemini quota)
Per-IP: 5 req/min burst 2, max 20/day
extractClientKey — gets client IP from X-Forwarded-For / X-Real-IP / RemoteAddr
getLimiter — creates/returns per-IP limiter entry (capped at 10k entries)
StartCleanup — background goroutine, every 5 min removes entries idle >30 min

===============================================
Handlers (HTTP layer)
================================================
handlers/handlers.go

setHeaders — sets CORS + SSE headers, handles OPTIONS preflight
allowedOrigin — validates origin is localhost only
validateTextReq → chains:
decodeAndSanitize — JSON decode + trim prompt
normalizeMessages — if no messages array, wraps prompt into one
validateMessageSize — rejects if total chars > 20k
GenerateText — handles POST /api/ai-assist → calls services.StreamLLM → pipes to streamSSE
GenerateImage — stubbed out, commented
handlers/ollama_handler.go

ollamaQueue — buffered channel of size 1 (semaphore), allows only 1 Ollama request at a time
GenerateOllamaText — handles POST /api/ollama → blocks on semaphore → calls services.StreamOllama → pipes to streamSSE
handlers/rag.go

RagIndex — handles POST /api/rag/index → calls services.IndexDocuments → returns JSON {ok, indexed, collection}
RagAsk — handles POST /api/rag/ask → calls services.AskRag → returns JSON {answer, contexts}
handlers/stream.go

streamSSE — shared by both GenerateText and GenerateOllamaText; reads from channel, writes each chunk as SSE data: lines, flushes immediately, sends event: end when channel closes
=================================================
                Services
=================================================
services/llm.go

StreamLLM — builds Gemini request, calls doGEMINIRequest, spawns goroutine with readGeminiSSEToChannel
readGeminiSSEToChannel — reads SSE lines from Gemini HTTP stream, extracts text, sends to channel
extractTextFromJSON — parses Gemini SSE JSON payload, returns the text field
doGEMINIRequest — builds HTTP POST to Gemini API with retry via withRetry
buildGeminiContentsFromRequest / buildGeminiContents — converts TextRequest → Gemini API format (maps assistant role → model)
services/ollama.go

StreamOllama — builds Ollama request, calls doOllamaRequest, spawns goroutine with readOllamaToChannel
readOllamaToChannel — reads streaming JSON from Ollama, sends non-empty chunks to channel
doOllamaRequest — builds HTTP POST to Ollama /api/chat with retry
buildOllamaMessagesFromRequest / buildOllamaMessages — converts TextRequest → Ollama format, prepends system prompt
services/rag.go

IndexDocuments — filters empty docs, then either routes to Python RAG service (usePythonRag) OR: calls ensureCollection → embedTexts → upserts to ChromaDB
AskRag — either routes to Python RAG OR: queryContexts (embed question → query Chroma) → askOllama (non-streaming) with injected context prompt
embedTexts — calls Ollama /api/embed to get vector embeddings
ensureCollection — creates ChromaDB collection if not exists
askOllama — non-streaming Ollama chat call (used only by RAG)
doJSON — generic HTTP helper used by all RAG functions
Config helpers: ragBackend, pyRagURL, chromaURL, ollamaURL, embedModelName, chatModelName
services/retry.go

withRetry — retries a request up to 3 times with exponential backoff (1s→2s→4s), only for 429/503/504
services/history.go

Placeholder only — SaveChatToDB stub, DB history not yet implemented
=================================================
Models (data shapes)
=================================================
models/request.go — TextRequest, Message, Role, ImageRequest

models/rag.go — RagIndexRequest, RagAskRequest, RagAskResponse
=================================================
HTTP POST
  → ErrorRecovery (panic guard)
  → RateLimiter (global + per-IP + daily)
  → Handler (validate → service call)
      ├─ /api/ai-assist   → StreamLLM    → Gemini API  → streamSSE → client
      ├─ /api/ollama      → StreamOllama → Ollama API  → streamSSE → client
      ├─ /api/rag/index   → IndexDocuments → Ollama (embed) + ChromaDB → JSON
      └─ /api/rag/ask     → AskRag → Ollama (embed+chat) + ChromaDB → JSON

                