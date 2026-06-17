rag db populate flow:
Populate PostgreSQL
  cat prisma/seed-qa-pairs.sql | docker compose exec -T postgres psql -U postgres transcendance_db

 curl -X POST http://localhost:8090/admin/reload-from-db \
    -H "X-Admin-Token: change-me-before-deploy"
!!! nb: add cmds!! to show this todo!!
===================================
  docker system prune          # removes stopped containers, dangling
  images, unused build cache
  docker builder prune         # build cache only
  docker system prune -a       # everything not currently in use
  (aggressive)
===================
docker compose restart python-rag
docker compose logs python-rag -f --since 0s
====================
docker compose up --build --force-recreate llm-server -d
==========================================================
!!!NB!!!
docker system df -v // disk free
get info on docker images, voluesm build cache
=========================
git push origin --delete 31-rag-improve  // delete remote branch
============================
git fetch origin
git checkout remote-new-branch
=====================================================
for go we do need to recompile, didnt install an extra tool: 
docker compose -d --build llm-server
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