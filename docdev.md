best: use docker builder prune
during all container running: to clear build up cache etc which grows to 30 and more gb
other option:
docker system prune -af --volumes
===================
!!!NB!!!
docker system df -v
get info on docker images, voluesm build cache
=========================

For development, there is an extra docker-compose.dev.yml file that enables live reload for both Python and the app. This means code changes are reflected immediately in the local browser, without needing to rebuild the containers:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
base stack only: (production)
docker compose up --build
=====================================================
docker system prune -af --volumes 
then:
docker compose build --no-cache && docker compose up -d
=====================================================

Use --build only when you changed:
Dockerfile/base image
package.json or lockfile
Anything copied during image build that is not from the live mount
================================
for go we do need to recompile, didnt install an extra tool: 
docker compose -d --build --no-cache llm-server
or:
docker compose up -d llm-server
==================================
for debugg:
docker compose logs -f app llm-server python-rag
================================
restart only app service:
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart app

if changed dependencies or dockerfiles, also restart llm-server and python-rag:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build app
================================
sudo systemctl start docker
===
sudo dockerd &

It manually starts the Docker daemon process in the background (& = background).

The daemon is the service that actually runs containers — the docker CLI  installed is just a client that talks to it. Without the daemon running, the CLI can't do anything.

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
docker system prune -af --volumes --no-cache

====================================

//shows disk usage broken down by images, containers, volumes, and build cache.
docker system df // disk free

docker pull ollama/ollama:0.20.5
// it fails again, the tag 0.20.5 may be broken on the registry. In that case, check your docker-compose.yml and try switching to ollama/ollama:latest or a nearby stable tag.

docker compose logs python-stt
docker compose up -d --build caddy app

for deleted files:
git add -A
==============================
docker exec 42overflow-ollama-1 ollama list
// shows the models currently available in the Ollama container
==============

if running on a machine with an NVIDIA GPU : 
 docker compose -f docker-compose.yml -f docker-compose.gpu.yml up
 =================
 replace llm
 ================= 
  # 1. Remove old model
  docker exec 42overflow-ollama-1 ollama rm gemma3:1b

  # 2. Pull new model
  docker exec 42overflow-ollama-1 ollama pull gemma3:4b

  After that, verify it's there:

  docker exec 42overflow-ollama-1 ollama list