 1. Browser → Caddy → SvelteKit (/api/ai-assist)
  2. SvelteKit checks session via better_auth → 401 if not logged in
  3. SvelteKit forwards to http://llm-server:8081 with header X-Internal-Secret: <secret from .env>
  4. Go InternalSecret middleware checks that header → 403 if missing or wrong
  5. Request reaches rate limiter + handler

  Why it matters:

  llm-server is on the internal Docker network — not exposed to the internet. But any container on app-net could call it directly, bypassing auth
  entirely. The secret proves the request came through SvelteKit (which already verified the user), not from some other container or someone who
  found the internal port. It's a cheap trust boundary inside the network.