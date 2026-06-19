#!/bin/bash

# run in terminal first:  
docker compose cp llm-system-interface/test_api.sh llm-server:/tmp/test_api.sh
docker compose exec llm-server sh /tmp/test_api.sh


# run: ./llm-system-interface/test_api.sh

# Configuration
API_URL="http://localhost:8081/api/ai-assist"
SECRET=${LLM_INTERNAL_SECRET:-$(grep LLM_INTERNAL_SECRET llm-system-interface/.env | cut -d= -f2)}
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#echo -e "${BLUE}--- Starting Llm sys interface: prompt: hi ---${NC}\n"
#curl -X POST $API_URL \
#     -H "Content-Type: application/json" \
#	 -H "X-Internal-Secret: ${SECRET}" \
#     -d '{"prompt": "Hi", "stream": false}'

#echo -e "${BLUE}--- Test 2 SSE STREAM: ---${NC}\n"
#curl -N -X POST $API_URL \
#     -H "Content-Type: application/json" \
#	 -H "X-Internal-Secret: ${SECRET}" \
#     -d '{"prompt": "Tell me a long story", "stream": true}'

#echo -e "${GREEN}[TEST 2] Empty Prompt:${NC}"
#curl -X POST $API_URL \
#     -H "Content-Type: application/json" \
#	 -H "X-Internal-Secret: ${SECRET}" \
#     -d '{"prompt": ""}'
#echo -e "\n"

## 3. Malformed JSON (Error Handling)
#echo -e "${GREEN}[TEST 3] Bad JSON:${NC} Sending broken syntax..."
#curl -X POST $API_URL \
#     -H "Content-Type: application/json" \
#	 -H "X-Internal-Secret: ${SECRET}" \
#     -d '{"prompt": "broken" ' # Missing closing brace
#echo -e "\n"

## 4. Large Payload (Stress Test)
echo -e "${GREEN}[TEST 4] Large Payload:${NC} Sending 5000 repetitions of 'meow'... llm responses coincise as per internal prompt"
LONG_PROMPT=$(printf 'meow %.0s' {1..5000})
curl -X POST $API_URL \
     -H "Content-Type: application/json" \
	 -H "X-Internal-Secret: ${SECRET}" \
     -d "{\"prompt\": \"$LONG_PROMPT\"}"
echo -e "\n"

## 5. Rate Limit Simulation (Rapid Fire)
echo -e "${GREEN}[TEST 5] Rate Limiting:${NC} Blasting 5 requests in 1 second..."
for i in {1..5}; do
  curl -s -X POST $API_URL \
       -H "Content-Type: application/json" \
	   -H "X-Internal-Secret: ${SECRET}" \
       -d "{\"prompt\": \"Spam request $i\"}" &
done
wait
echo -e "\n\n${BLUE}--- Tests Completed ---${NC}"