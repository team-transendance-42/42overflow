Open your terminal (WSL/Ubuntu).

Open 5 separate tabs or windows.

Make sure your Docker containers are running: docker-compose up -d.
================================

use this command in every terminal. It sends a POST request with a JSON body to your local server.
curl -X POST http://localhost:8080/api/ollama \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Explain quantum physics in 1 sentence"}'
     ================================

Step 3: Run the Test
To see the Queue and Rate Limiter in action, follow this timing:

Terminal 1: Press Enter. (Ollama starts working).

Terminal 2: Press Enter immediately after.

Expectation: This terminal should "hang" (wait). This proves your Ollama Queue (Semaphore) is working.

Terminal 3: Press Enter.

Expectation: If your rate limit is "2 per minute," this one might get an immediate 429 Too Many Requests error.

Terminal 4 & 5: Press Enter.

Expectation: These should definitely fail with 429.
================================

What to look for in the logs
While the terminals are running, open a 6th terminal and watch the server logs:
docker compose logs -f llm-server

GenerateOllamaText(): method=POST (Student 1 starts).

GenerateOllamaText(): method=POST (Student 2 arrives and waits).

Rate limit exceeded (2/min) (Student 3 gets blocked by your middleware).

Ollama slot released (Student 1 finishes).
================================

The "One-Liner" Stress Test
If you don't want to click 5 terminals manually, you can run this single command to fire 5 requests at once:

for i in {1..5}; do curl -X POST http://localhost:8080/api/ollama -H "Content-Type: application/json" -d '{"prompt":"Hi"}' & done

The & at the end tells Linux to run all 5 in the background simultaneously.
     