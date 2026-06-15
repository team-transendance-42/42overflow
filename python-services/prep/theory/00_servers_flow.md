Browser → Caddy :8080 → SvelteKit :5173 → llm-server / python-stt (internal)


  Caddy's current job is just:
  - Compression (gzip/zstd)
  - Cache headers for /assets/*
  - Single public entry point (only port 8080 is exposed)

  SvelteKit handles all routing and auth.

===============
  Pros of keeping Caddy

  ┌─────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │                     │                                                                                                        │
  ├─────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ TLS in production   │ Caddy auto-renews Let's Encrypt certs. SvelteKit/Node cannot do this.                                  │
  ├─────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Static file serving │ In production build, Caddy serves /assets/* directly from disk — Node never touched. Faster, less CPU. │
  ├─────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Compression at edge │ Offloads gzip from Node's single thread                                                                │
  ├─────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Future flexibility  │ Add rate limiting, security headers, DDoS protection at one place without touching app code            │
  └─────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────┘
  ==================
 Cons of keeping Caddy

  - Extra container, extra debugging hop
  - For small learning project, it's overhead
  - Makes "why isn't my request reaching the app" harder to trace
===========
  In real production — always keep a proxy
  
  Node.js is single-threaded. In production you always put something (Caddy, Nginx, a load balancer) in front of it. TLS alone is reason enough —
  you never expose a raw Node server to the internet.
============

  How secure is SvelteKit server routes
  
  Solid for what they do. Server routes (+server.ts) run in Node.js on the server — the browser never sees their code or env vars. Your proxyLLM
  auth check is simple and correct: no user = 401, no secret = 500.
  
  The weakness isn't SvelteKit — it's Node.js being single-threaded. One slow/stuck request can block others. That's another reason to keep Caddy:
  it handles connection management and can timeout/kill stuck upstream connections before they pile up.

