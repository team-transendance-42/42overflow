 ---
  Container Architecture Overview

  Browser
    └── Caddy :8080 (reverse proxy, gzip)
          ├── /api/*      → llm-server (Go) :8081
          ├── /stt/*      → python-stt (Whisper) :8091
          └── /*          → app (SvelteKit) :5173

  llm-server ──► python-rag (FastAPI) :8090
                      └──► chromadb (vector DB) :8000
                      └──► ollama (LLM inference) :11434

  python-stt ──► (Whisper model from volume cache)
  ollama-init ──► ollama (pulls model weights once at startup)
  postgres :5433 ──► app (SvelteKit/adapter-node)
  ====================
   Pros:

  - Single responsibility — each service does one thing; a crash in STT
  doesn't kill RAG or the Go server
  - Independent rebuild/redeploy — update only what changed
  - Correct startup ordering — depends_on with condition:
  service_healthy ensures no race conditions at boot
  - Security surface isolation — internal services use expose, not
  ports; only Caddy and Postgres are host-accessible
  - Separate scaling — in theory you could scale python-rag
  independently if RAG load spikes
  - Standard patterns — init-container for model pull, named volumes for
   data persistence, Caddy for edge concerns (gzip, header forwarding)

  Cons:

  - Operational overhead — 9 containers to manage, debug, monitor; more
  things that can fail
  - Network latency — every call crosses a container boundary; Go →
  Python RAG → ChromaDB is 2 extra hops versus 1 in-process library
  - Resource consumption — each container has its own overhead; on a
  single machine (local dev/small server) this adds up
  =================
   1. Missing multi-stage build in Go Dockerfile (significant)

  golang:1.25-alpine as the final image ships the entire Go toolchain
  (~300 MB). A multi-stage build drops this to ~10 MB:

  FROM golang:1.25-alpine AS builder
  WORKDIR /app
  COPY go.mod go.sum ./
  RUN go mod download
  COPY . .
  RUN go build -o llm_server llm_server.go

  FROM alpine:3.20
  RUN apk add --no-cache curl ca-certificates
  COPY --from=builder /app/llm_server /llm_server
  EXPOSE 8081
  CMD ["/llm_server"]
  ==========================

   In docker-compose.yml (production), python-stt has volumes: -
  ./python-services/speach-to-text:/app, which means the Dockerfile's
  COPY . . is overridden at runtime — the baked image is never actually
  used. Every other service bakes source into the image. Pick one
  strategy and stick to it.
  =======================

  