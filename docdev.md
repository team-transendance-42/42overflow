For development, there is an extra docker-compose.dev.yml file that enables live reload for both Python and the app. This means code changes are reflected immediately in the local browser, without needing to rebuild the containers:

base stack only: (production)
docker compose up --build

dev stack with reload:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

If the progress output is too noisy, use detached mode and quiet build/pull flags:

docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --quiet-build --quiet-pull

Then follow only the services you care about:

docker compose logs -f app llm-server rag-python
================================
restart only app service:
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart app

if changed dependencies or dockerfiles, also restart llm-server and rag-python:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build app
================================

docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d app
================================

Use --build only when you changed:

Dockerfile/base image
package.json or lockfile
Anything copied during image build that is not from the live mount