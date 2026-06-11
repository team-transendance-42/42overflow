best: use docker builder prune
during all container running: to clear build up cache etc which grows to 30 and more gb
other option:
docker system prune -af --volumes
docker compose build --no-cache && docker compose up -d
===================
!!!NB!!!
docker system df -v // disk free
get info on docker images, voluesm build cache
=========================
git fetch origin
git checkout remote-new-branch
=====================================================
for go we do need to recompile, didnt install an extra tool: 
docker compose -d --build --no-cache llm-server
or:
docker compose up -d llm-server
==================================
for debugg:
docker compose logs -f app llm-server python-rag
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

==============================
docker exec 42overflow-ollama-1 ollama list
// shows the models currently available in the Ollama container
==================
 =================
 replace llm
 ================= 
  # 1. Remove old model
  docker exec 42overflow-ollama-1 ollama rm gemma3:1b

  # 2. Pull new model
  docker exec 42overflow-ollama-1 ollama pull gemma3:4b

  After that, verify it's there:
  docker exec 42overflow-ollama-1 ollama list