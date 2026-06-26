 !!NB!!
  Gemma3:4b — even at temp 0.3, this model ignores "reproduce
  the COMPLETE answer word for word" for long answers. It summarizes to the
  first sentence. This is a well-known limitation of small 4B models: they
  default to brevity regardless of instructions.
    Why it truncates every time, not randomly — temp 0.3 makes the model
  consistently pick the most probable (short) completion. At temp 0.8 it
  occasionally reproduced more, but also hallucinated. At temp 0.3 it reliably
  truncates but doesn't invent.
==============================================

 
 // replace <RAG_ADMIN_TOKEN> with the value of RAG_ADMIN_TOKEN in .env file
 
 // populate postgres db with test data: users, subjects, posts, comments: all needed for the rag testing
docker compose exec python-rag curl -s -X POST \
    http://localhost:8090/admin/seed-postgres \
    -H 'Content-Type: application/json' \
    -H 'X-Admin-Token: Tra-la-la' \
    -d '{}'

// take relevant info from postgres db and embed and store in chromadb
docker compose exec python-rag curl -s -X POST \
    http://localhost:8090/admin/sync-chroma \
    -H 'X-Admin-Token: Tra-la-la'

// delete info from postgres(subjects, posts, comments)
  docker compose exec python-rag curl -X POST http://localhost:8090/admin/wipe -H "X-Admin-Token: Tra-la-la"

//	smoke-test once Docker is running:
  docker compose exec python-rag curl -s http://localhost:8090/admin/metrics -H "X-Admin-Token: Tra-la-la" | python3 -m json.tool
bm25_only_fallbacks: 7 -> means the embedding model failed 7 times at query time — has_embeddings was False, meaning NumpyIndex returned no results
  (or the embed call threw), so retrieval fell back to keyword search (BM25) alone, with no dense/semantic component.
debug:
docker compose logs python-rag | grep "embedding failed\|dense search failed"
or
docker compose logs python-rag | grep -E "\[startup\]|\[indexer\]|numpy|indexed"


  docker compose logs -f python-rag

  How does poll() work and why is non-blocking I/O required for webserv?

====================
## Commented-out: Two-tier RAG optimization — llm-system-interface/services/rag.go (StreamRagAnswer)

### Tier 1 — Direct bypass (similarity >= 0.85)
Location: after the semantic gate, before building context blocks.
What it does: when the question is near-identical to a stored doc, skips Ollama entirely
and returns the stored answer verbatim prefixed with "From community: ", then caches it.
Eliminates LLM non-determinism for exact repeated questions — no hallucination possible.
Why disabled: need to validate the similarity threshold (0.85) against real data first.

### Tier 2 — Lower temperature for Ollama (0.55–0.85 similarity)
Location: Ollama request body construction (ollamaReq map).
What it does: adds "options": {"temperature": 0.3} to the Ollama JSON body when
has_embeddings=true. Default Ollama temp is 0.8 (high randomness). 0.3 makes the
model more deterministic — same question is more likely to get the same answer.
Alternative simpler approach: set temperature 0.3 for ALL calls unconditionally
(remove the has_embeddings check) — same benefit, less code.
====================
clear and restart chromadb:

  docker compose exec 0.chromadb /bin/sh -c "rm -rf /chroma/chroma/*"
  docker compose restart chromadb
  docker compose exec python-rag curl -s -H "X-Admin-Token: Tra-la-la" \
    -X POST http://localhost:8090/admin/sync-chroma | python3 -m json.tool




