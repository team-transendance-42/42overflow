for python and app code: no need to rebuild the image or restart the container in dev mode. it all shows automatically.

Exceptions (When you MUST run a command):
1. If you add a new library (Pip/UV or NPM):
Docker doesn't know about new packages until you rebuild the image.

docker compose up -d --build app (for Node)

docker compose up -d --build python-rag (for Python)

2. If you change your Prisma Schema:
Since your entrypoint.sh runs prisma generate, you just need to restart the container:
========================================
docker compose logs -f llm-server
========================================

docker compose restart app

3. If the container crashes or gets stuck:

docker compose restart <service-name>

The "Developer View" Command
Keep this running in a second terminal window to see errors immediately as you save files:
docker compose logs -f app python-rag python-stt
============================
!!NB!!
=============================
For Go code, the strategy is different because Go is a compiled language. You don't want to rebuild the container every time; you want to recompile the binary inside the container.

To prevent your WSL from crashing again, you need to use Hot Reloading and regular Pruning.
===============================
 "No-Rebuild" Strategy (Hot Reload)
To avoid manual rebuilds, most Go developers use a tool called Air. It watches your .go files and re-compiles instantly when you save.
=================================
--build: Only rebuilds what has changed. It keeps the cache, so it stays fast.
=================================

How to stop WSL from crashing (The Real Problem)
WSL "crashes" because it tries to take all your Windows RAM for itself. Docker doesn't usually crash WSL; WSL's default settings do.

The Fix: Create a file in your Windows user folder (e.g., C:\Users\YourName\.wslconfig) and limit the RAM:

Ini, TOML
[wsl2]
memory=4GB   # Limits WSL to 4GB RAM
processors=2 # Limits WSL to 2 CPU cores