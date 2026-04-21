For development, there is an extra docker-compose.dev.yml file that enables live reload for both Python and the app. This means code changes are reflected immediately in the local browser, without needing to rebuild the containers:
==============================
docker compose build --no-cache llm-server
docker compose up -d llm-server
==================================

base stack only: (production)
docker compose up --build

dev stack with reload:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

If the progress output is too noisy, use detached mode and quiet build/pull flags:

docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --quiet-build --quiet-pull

Then follow only the services you care about:

docker compose logs -f app llm-server python-rag
================================
restart only app service:
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart app

if changed dependencies or dockerfiles, also restart llm-server and python-rag:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build app
================================

docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d app
================================

Use --build only when you changed:

Dockerfile/base image
package.json or lockfile
Anything copied during image build that is not from the live mount
================================
sudo systemctl start docker
===
sudo dockerd &

It manually starts the Docker daemon process in the background (& = background).

The daemon is the service that actually runs containers — the docker CLI you have installed is just a client that talks to it. Without the daemon running, the CLI can't do anything.

====
docker ps -a
docker images
docker volume ls

Remove all stopped containers:
docker container prune

Remove unused images:
docker image prune
Remove unused volumes:
docker volume prune

// for development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build llm-server
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f llm-server
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f llm-server
=================================

docker container prune -f
docker image prune -a -f
docker volume prune -f
docker network prune -f
===================================
Remove everything (be careful!):
docker system prune -af
====================================
no python recompile if u run:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
===================================================================

docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build llm-server

go install golang.org/x/tools/gopls@latest

//shows disk usage broken down by images, containers, volumes, and build cache.
docker system df // disk free

docker pull ollama/ollama:0.20.5
// it fails again, the tag 0.20.5 may be broken on the registry. In that case, check your docker-compose.yml and try switching to ollama/ollama:latest or a nearby stable tag.

docker compose logs python-stt
docker compose up -d --build caddy app

