Goal Architecture

Browser talks only to Nginx on ports 80 and 443.
Nginx forwards:
/ to app service on internal port 5173
/api to llm-server service on internal port 8081
Ollama stays internal-only on 11434 and is never public.
So traffic flow is:
Client -> Nginx -> app or llm-server -> ollama

Why This Helps

Security and control:

One place for rate limits
Max request/body size limits
Security headers
Basic auth on selected paths
IP allow/deny rules
Hide internal ports from the internet
Performance:

Compression with gzip (and brotli if enabled)
Static asset caching
Better connection handling and buffering

Clean URLs:

Users see one domain only
No exposed internal ports like 5173, 8081, 11434
Stable URL structure regardless of backend changes
Step 1: Compose Strategy
Use only Nginx as published service:

Publish Nginx 80 and 443
Use expose for app and llm-server (internal)
Keep ollama internal (expose or even no expose; service-name networking still works)
=============================

Step 2: Nginx Config Basics
Create nginx.conf with:

Upstreams for app and llm-server
Path routing
Security headers
Rate limits
Request size limits
Compression
Cache for static files

worker_processes auto;

events { worker_connections 1024; }

http {
  include       /etc/nginx/mime.types;
  default_type  application/octet-stream;
  sendfile on;
  tcp_nopush on;
  tcp_nodelay on;
  keepalive_timeout 65;
  server_tokens off;

  # Rate limit zones
  limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
  limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

  # Compression
  gzip on;
  gzip_comp_level 5;
  gzip_min_length 1024;
  gzip_types
    text/plain text/css application/json application/javascript
    text/xml application/xml application/xml+rss image/svg+xml;

  # Upstreams
  upstream app_upstream {
    server app:5173;
  }

  upstream llm_upstream {
    server llm-server:8081;
  }

  server {
    listen 80;
    # listen 443 ssl http2; # enable when TLS is ready
    # ssl_certificate /etc/nginx/certs/fullchain.pem;
    # ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Global limits
    client_max_body_size 2m;
    limit_conn conn_limit 20;

    # API route
    location /api/ {
      limit_req zone=api_limit burst=20 nodelay;

      proxy_pass http://llm_upstream;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_read_timeout 300s;
    }

    # Static cache hints
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2)$ {
      proxy_pass http://app_upstream;
      expires 7d;
      add_header Cache-Control "public, max-age=604800, immutable";
      access_log off;
    }

    # App route
    location / {
      proxy_pass http://app_upstream;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Optional protected admin
    # location /admin/ {
    #   auth_basic "Restricted";
    #   auth_basic_user_file /etc/nginx/.htpasswd;
    #   proxy_pass http://app_upstream;
    # }

    # Optional IP allowlist for sensitive endpoint
    # location /api/internal/ {
    #   allow 10.0.0.0/8;
    #   deny all;
    #   proxy_pass http://llm_upstream;
    # }
  }
}
===========================================

ep 3: Security Patterns You Can Add

Rate limit:
limit_req_zone + limit_req in API locations
Prevent abuse and brute-force style floods
Request limits:
client_max_body_size to block oversized requests
Helps avoid memory abuse and accidental huge uploads
Headers:
X-Content-Type-Options, X-Frame-Options, Referrer-Policy
Reduce common browser attack surface
Auth:
Basic auth for admin paths
Easy first layer before full auth system
IP rules:
allow and deny in critical routes
Good for internal/debug/admin endpoints
Step 4: Performance Patterns

Gzip:
Good default, widely supported
Useful for JSON, CSS, JS
Brotli:
Better compression than gzip for text
Requires Nginx image/module support
If unavailable, keep gzip only
Caching:
Cache versioned static assets for days
Keep API responses uncached by default unless explicitly safe
Timeouts and buffering:
Adjust proxy_read_timeout for LLM responses
Prevent premature timeout on long generation
Step 5: Clean URL Strategy

Keep app under /.
Keep backend under /api/.
Do not expose app 5173 or llm-server 8081 publicly.
Keep ollama private and only reachable from llm-server via service name ollama:11434.
===============================
This gives one consistent public base URL and isolates internal topology.

Step 6: TLS in Real Deployments

Enable 443 in Nginx.
Add real certificates.
Redirect 80 -> 443.
Keep HSTS only after HTTPS is stable.
Common Pitfalls

WebSocket/HMR in dev:
If using Vite dev behind Nginx, keep upgrade headers (already shown).
Trailing slash mismatches:
Be consistent in proxy_pass and location definitions.
Accidentally exposing internal services:
Avoid ports on llm-server and ollama unless debugging from host.
Over-aggressive caching:
Never cache dynamic API blindly.