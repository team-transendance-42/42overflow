#!/bin/sh
set -e
MODEL="${OLLAMA_MODEL:-qwen2.5-coder:7b}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"
OLLAMA_URL="${OLLAMA_URL:-http://ollama:11434}"

model_exists() {
  name="$1"
  # tr strips all whitespace so the match holds regardless of JSON formatting (e.g. "name": "..." vs "name":"...")
  curl --fail --silent --show-error "$OLLAMA_URL/api/tags" |
    tr -d ' \t' | grep -Fq "\"name\":\"$name\""
}

pull_model() {
  name="$1"

  if model_exists "$name"; then
    echo "Model already present: $name"
    return 0
  fi

  echo "Pulling model: $name"

  retries=3
  attempt=0
  while [ $attempt -lt $retries ]; do
    attempt=$((attempt + 1))
    if curl --fail --silent --show-error -X POST "$OLLAMA_URL/api/pull" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$name\"}"; then
      return 0
    fi
    echo "Pull attempt $attempt/$retries failed for $name"
    [ $attempt -lt $retries ] && sleep 5
  done
  echo "ERROR: failed to pull $name after $retries attempts" >&2
  return 1
}

pull_model "$MODEL"

if [ "$EMBED_MODEL" != "$MODEL" ]; then
  pull_model "$EMBED_MODEL"
fi

echo "Done. Chat and embedding models are ready."