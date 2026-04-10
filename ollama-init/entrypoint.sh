#!/bin/sh
set -e
MODEL="${OLLAMA_MODEL:-qwen2.5-coder:7b}"
OLLAMA_URL="${OLLAMA_URL:-http://ollama:11434}"

echo "Pulling model: $MODEL"

curl --fail --silent --show-error -X POST "$OLLAMA_URL/api/pull" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$MODEL\"}"

echo "Done."