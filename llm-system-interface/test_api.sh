#!/bin/bash

# Configuration
API_URL="http://localhost:8081/ai-assist"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}--- Starting Zombie Kittens API Tests ---${NC}\n"

# To test standard JSON (what Svelte uses now)
curl -X POST $API_URL \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hi", "stream": false}'

# To test the "Kitten Stream" (SSE)
curl -N -X POST $API_URL \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Tell me a long story", "stream": true}'

# 1. Happy Path
# Use -N (no-buffer) to see the stream immediately
echo -e "${GREEN}[TEST 1] Happy Path:${NC} Asking a normal question..."
curl -N -X POST $API_URL \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Who are the Zombie Kittens?"}'
echo -e "\n"

# 2. Empty Prompt (Edge Case)
echo -e "${GREEN}[TEST 2] Empty Prompt:${NC} Sending empty string..."
curl -X POST $API_URL \
     -H "Content-Type: application/json" \
     -d '{"prompt": ""}'
echo -e "\n"

# 3. Malformed JSON (Error Handling)
echo -e "${GREEN}[TEST 3] Bad JSON:${NC} Sending broken syntax..."
curl -X POST $API_URL \
     -H "Content-Type: application/json" \
     -d '{"prompt": "broken" ' # Missing closing brace
echo -e "\n"

# 4. Large Payload (Stress Test)
echo -e "${GREEN}[TEST 4] Large Payload:${NC} Sending 5000 repetitions of 'meow'..."
LONG_PROMPT=$(printf 'meow %.0s' {1..5000})
curl -X POST $API_URL \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"$LONG_PROMPT\"}"
echo -e "\n"

# 5. Rate Limit Simulation (Rapid Fire)
echo -e "${GREEN}[TEST 5] Rate Limiting:${NC} Blasting 5 requests in 1 second..."
for i in {1..5}; do
  curl -s -X POST $API_URL \
       -H "Content-Type: application/json" \
       -d "{\"prompt\": \"Spam request $i\"}" &
done
wait
echo -e "\n\n${BLUE}--- Tests Completed ---${NC}"