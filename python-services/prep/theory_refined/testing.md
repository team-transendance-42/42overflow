Exact hit: Question verbatim from seed -> Full answer
Paraphrise hit: "how do goroutines work" when seed has a goroutines Q&A-> Full answer
out of scope: whats capital of france -> refused
gray area: topic in docs, subtopic not -> gemma says not enough context
===================
# Test retrieval directly
  curl -s -X POST http://localhost:8090/rag/retrieve \
    -H 'Content-Type: application/json' \
    -d '{"question": "what is malloc"}' | jq .

  # Test off-topic is rejected
  curl -s -X POST http://localhost:8090/rag/retrieve \
    -H 'Content-Type: application/json' \
    -d '{"question": "what is the meaning of life"}' | jq .confidence

  # Health check with doc count
  curl -s http://localhost:8090/healthz | jq .

  Key things to verify manually:
  1. A topic-specific question returns docs from the right topic (check "topic" in contexts)
  2. An off-topic question returns confidence < 0.020 or best_similarity < 0.55 
  3. A question already answered returns instantly (cache hit)
  4. The Go streaming endpoint returns tokens progressively, not all at once

