#!/bin/sh
set -e
MODEL="${OLLAMA_MODEL:-qwen2.5-coder:7b}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"
OLLAMA_URL="${OLLAMA_URL:-http://ollama:11434}"

model_exists() {
  name="$1"
  curl --fail --silent --show-error "$OLLAMA_URL/api/tags" |
    grep -Fq "\"name\":\"$name\""
}

pull_model() {
  name="$1"

  if model_exists "$name"; then
    echo "Model already present: $name"
    return 0
  fi

  echo "Pulling model: $name"

  curl --fail --silent --show-error -X POST "$OLLAMA_URL/api/pull" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\"}"
}

pull_model "$MODEL"

if [ "$EMBED_MODEL" != "$MODEL" ]; then
  pull_model "$EMBED_MODEL"
fi

echo "Done. Chat and embedding models are ready."