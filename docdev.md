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
## Delete the stale collection
	docker compose stop chromadb
  docker volume rm 42overflow_chroma-data
  docker compose up -d chromadb


---

## RAG — Sync & Populate


**Files involved:**
- `reload_rag.sh` — calls the RAG admin endpoint to reload from DB (run from project root)
- `python-services/rag/dev_populate.py` — inserts fake users/posts/comments into Postgres for testing
- `llm-system-interface/.env` — contains `RAG_ADMIN_TOKEN` (token is hardcoded in `reload_rag.sh`)
- `python-services/rag/seed/` — static Q&A seed data loaded at RAG startup (not from DB)

> **Note:** A post must have at least one comment to be picked up by the RAG.

### 1. Reload RAG from real DB posts only

```bash
bash reload_rag.sh
```

### 2. Insert fake dev data (HappyFace22, Revolution12, Mystery User) then reload

```bash
# First time (or to add more posts without wiping existing ones):
cd python-services/rag && uv run python dev_populate.py && cd ../..
bash reload_rag.sh

# Re-insert clean (wipes all fake posts first, then re-inserts):
cd python-services/rag && uv run python dev_populate.py --clean && cd ../..
bash reload_rag.sh
```

`dev_populate.py` connects to Postgres on **localhost:5433** (the host-mapped port).
The stack must be running. Run it from the host, not inside a container.

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
