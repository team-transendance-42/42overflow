# Docker Cheatsheet

---

## Inspect & Monitor

```bash
docker ps -a                        # list all containers
docker images                       # list images
docker volume ls                    # list volumes
docker system df                    # disk usage (images, containers, volumes, build cache)
docker system df -v                 # verbose disk usage breakdown
docker compose logs -f app llm-server python-rag   # follow logs for services
```

---

## Cleanup — Targeted

```bash
docker container prune              # remove stopped containers
docker container prune -f           # same, no confirmation prompt
docker image prune                  # remove dangling images
docker image prune -a -f            # remove all unused images
docker volume prune -f              # remove unused volumes
docker network prune -f             # remove unused networks
docker builder prune                # build cache only  ← best for reclaiming build cache (can grow 30GB+)
```

## Cleanup — Aggressive

```bash
docker system prune                 # stopped containers, dangling images, unused build cache
docker system prune -a              # everything not currently in use
docker system prune -af --volumes   # everything including volumes (be careful!)
```

---

## Build & Start

```bash
# Production stack
docker compose up --build

# Fresh build, no cache (use after prune)
docker compose build --no-cache && docker compose up -d

# Use --build only when you changed:
#   - Dockerfile / base image
#   - package.json or lockfile
#   - Anything COPYed during image build (not from a live mount)
```

---

## Rebuild Specific Services

```bash
# Go service (requires recompile — no live-reload tool installed)
docker compose up -d --build --no-cache llm-server

# Frontend / Caddy
docker compose up -d --build caddy app
```

---

## Docker Daemon (if not running)

```bash
sudo systemctl start docker         # preferred: start via systemd
sudo dockerd &                      # fallback: start daemon manually in background
```

---

## RAG DB — Populate

```bash
# Reload RAG service from DB
curl -X POST http://localhost:8090/admin/reload-from-db \
  -H "X-Admin-Token: change-me-before-deploy"

# Dev: populate with fake data then reload
cd python-services/rag && uv run python dev_populate.py && cd ../.. && \
docker compose exec python-rag curl -s -X POST \
  http://localhost:8090/admin/reload-from-db \
  -H 'X-Admin-Token: My!Favourite-RAG-Token-Is-Longer-Than-Your-Entire-Codebase~42overflow'

# Production: reload from real DB only
docker compose exec python-rag curl -s -X POST \
  http://localhost:8090/admin/reload-from-db \
  -H 'X-Admin-Token: My!Favourite-RAG-Token-Is-Longer-Than-Your-Entire-Codebase~42overflow'
```

---

## Ollama / LLM Model Management

```bash
# List models in Ollama container
docker exec 42overflow-ollama-1 ollama list

# Switch model (example: gemma3:1b → gemma3:4b)
docker exec 42overflow-ollama-1 ollama rm gemma3:1b
docker exec 42overflow-ollama-1 ollama pull gemma3:4b
docker exec 42overflow-ollama-1 ollama list   # verify

# Pull a specific tag (check registry if tag is broken — try :latest as fallback)
docker pull ollama/ollama:latest
```

---
