======================================
   Stack is split into four layers
======================================

nginx is the only public entry point.
app is the Svelte frontend development server.
llm-server is the Go API layer that talks to Gemini and Ollama.
Ollama and Postgres are backend services used by llm-server and the app.

So the browser does not talk directly to Gemini, Ollama, or Postgres. It talks to nginx, and nginx routes traffic to the right internal service.
------------------------------------------------------
nginx.conf defines two upstreams:

app at app:5173
llm-server at llm-server:8081
Requests to /api/ go to llm-server.

Everything else goes to app.

docker-compose.yml wires the services together.

postgres is for now the db database.
app is the frontend dev server.
llm-server is the Go backend for AI requests.
ollama is the local model runtime.
ollama-init pulls the model into the Ollama volume.
nginx exposes the whole stack on host port 8080.
----------------------------------------------------
For a user opening the site:

Browser hits localhost:8080.
nginx receives the request on container port 80.
If the path is not /api/, nginx forwards it to app:5173.
The app renders the Svelte UI.
When the user submits a prompt, the frontend sends a request to /api/ai-assist or /api/ollama.
nginx forwards that API request to llm-server:8081.
llm-server decides whether to use Gemini or Ollama.
The answer streams back to the frontend.
The frontend parses the stream and updates the UI progressively.
-----
For Gemini, the chain is:

Frontend -> nginx -> llm-server
llm_server.go starts the Go service and registers routes.
handlers/handlers.go handles /api/ai-assist.
services/llm.go builds the Gemini request, sends it, and reads the streaming SSE response.
The handler converts that stream into SSE again for the browser.
So llm-server is not the model itself. It is the adapter and orchestrator
---

For Ollama, the chain is:

Frontend -> nginx -> llm-server
handlers/ollamahandler.go handles /api/ollama.
services/ollama.go sends the prompt to Ollama’s /api/chat endpoint.
The Ollama response is streamed back to the browser using SSE.
--------------------
nginx is only the traffic director. It does not:

validate requests
decide between Gemini and Ollama
enforce prompt limits
transform response formats
implement rate limiting logic
isolate provider-specific code
That is exactly what llm-server is for. It keeps provider logic out of the frontend and out of nginx.
=================
Good parts:

nginx is a clean single entry point.
the frontend is decoupled from provider details.
llm-server gives you one place to switch between Gemini and Ollama.
Ollama runs inside Docker, so models persist in the ollama-data volume.
ollama-init makes model setup repeatable.
SSE streaming gives a better user experience than waiting for a full response.
-----------------------
Areas for improvement:
Good parts:

nginx is a clean single entry point.
the frontend is decoupled from provider details.
llm-server gives you one place to switch between Gemini and Ollama.
Ollama runs inside Docker, so models persist in the ollama-data volume.
ollama-init makes model setup repeatable.
SSE streaming gives a better user experience than waiting for a full response.




