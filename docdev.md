For development, there is an extra docker-compose.dev.yml file that enables live reload for both Python and the app. This means code changes are reflected immediately in the local browser, without needing to rebuild the containers:

base stack only: (production)
docker compose up --build

dev stack with reload:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build