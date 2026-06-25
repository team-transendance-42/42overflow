browser access during dev, add this in docker-compose.yml temporarily:

  python-rag:
    ports:
      - "8090:8090"   # exposes to host — remove before prod

  Then http://localhost:8090/healthz and http://localhost:8090/metrics open directly in the browser.

in terminal any time:
docker compose exec python-rag curl -s http://localhost:8090/healthz | python3 -m json.tool

docker compose exec python-rag curl -s http://localhost:8090/metrics | python3 -m json.tool

