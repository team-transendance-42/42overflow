 in Caddyfile: The @static block — deep dive
  
  @static path /assets/* /favicon.ico /robots.txt
  header @static Cache-Control "public, max-age=31536000, immutable"

  What each word means:
  
  - public — this response can be stored in any cache, including shared caches like CDNs and ISP proxies. Without public, HTTPS responses default
  to private (browser-only cache).
  - max-age=31536000 — keep it for 31,536,000 seconds = exactly 1 year. The browser won't even send a request to the server; it just uses its
  local copy.
  - immutable — tells the browser "don't send a conditional request (If-None-Match) even when the cache is about to expire, because this file will
  never change." Without immutable, browsers send a check request at cache expiry even though the file hasn't changed. With it, they skip that
  round-trip entirely.

  Why it exists:
  Browsers re-download files unless told not to. On a repeat visit with no cache headers, the browser re-fetches every asset on every page load.
  That's slow and wastes bandwidth. This block tells browsers to load JS/CSS from disk instantly.
  
  The key assumption — Vite fingerprinting:
  This only works safely because Vite appends a content hash to every built asset filename: index-3f8a9c.js. When the file's content changes, the
  hash changes, the filename changes, the browser treats it as a new file and fetches it fresh. The old cache entry is simply never used again —
  it expires quietly after a year. This is why 1 year is safe for /assets/*.

  Pros:
  - Dramatically faster repeat visits — JS and CSS load from disk, not network
  - Reduces server load and bandwidth
  - Improves Lighthouse/Core Web Vitals scores
  - CDN-friendly (public allows CDN caching too)
  
  Cons/risks:

  ┌──────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │     File     │                                                    Risk                                                     │
  ├──────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ /assets/*    │ None — Vite-fingerprinted, safe to cache forever                                                            │
  ├──────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ /favicon.ico │ Low — rarely changes, but if you update it users see the old one for up to a year                           │
  ├──────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ /robots.txt  │ Real risk — if you urgently need to block a URL from indexing, the update won't be seen until cache expires │
  └──────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
  
  Edge cases:
  - immutable is ignored by Safari < 11 and IE — they fall back to max-age behaviour, which is fine
  - robots.txt — search engine crawlers (Googlebot) actually ignore Cache-Control on robots.txt and re-fetch it on their own schedule anyway. So
  the risk is mostly other crawlers and your own browser.
  - User-uploaded content (/uploads/) — this is NOT matched by @static, which is correct. You never want to cache user uploads aggressively since
  they can be replaced.
  - default-avatar.png (in your /static folder) — also NOT matched, also correct.
  
  Better alternatives for the non-fingerprinted files:
  
  Option A — split the matcher, shorter TTL for non-fingerprinted files:
  @assets path /assets/*
  header @assets Cache-Control "public, max-age=31536000, immutable"
  
  @misc path /favicon.ico /robots.txt
  header @misc Cache-Control "public, max-age=86400"
  86400 = 1 day. Reasonable for a favicon and robots.txt.
  
  Option B — drop /favicon.ico and /robots.txt from the rule entirely. Let SvelteKit serve them with its own headers (or no special headers).
  SvelteKit already sets Cache-Control: public, max-age=31536000, immutable on /_app/immutable/* assets in production builds. The only assets that
  need the Caddy rule are anything outside that path, which in this project is just /assets/* if that's where Vite outputs them.









delete:


 Remaining (7 steps):
  
  ┌─────┬────────────────────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────┐
  │  #  │                                      What                                      │                      File(s)                       │
  ├─────┼────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ 1   │ Generalize llmProxy.ts — targetUrl instead of hardcoded host, streaming        │ src/lib/server/llmProxy.ts + update 3 +server.ts   │
  │     │ option, pass Content-Type through                                              │ callers                                            │
  ├─────┼────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ 2   │ Add LLM_INTERNAL_SECRET to both .env files                                     │ .env + llm-system-interface/.env                   │
  ├─────┼────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ 3   │ Create STT proxy route                                                         │ src/routes/stt/convert_audio/+server.ts            │
  ├─────┼────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ 4   │ Add Go auth middleware                                                         │ llm-system-interface/middleware/auth.go (new file) │
  ├─────┼────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ 5   │ Update Go rate limiter — read user ID from context, remove OPTIONS bypass      │ middleware/ratelimiter.go                          │
  ├─────┼────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ 6   │ Wire InternalAuth before RateLimiter in server                                 │ llm-system-interface/llm_server.go                 │
  ├─────┼────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
  │ 7   │ Update Caddyfile — remove @stt+@api blocks, flush_interval -1, Option A static │ Caddyfile                                          │
  │     │  caching                                                                       │                                                    │
  └─────┴────────────────────────────────────────────────────────────────────────────────┴────────────────────
























