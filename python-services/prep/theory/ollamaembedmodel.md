OLLAMA_EMBED_MODEL is the model that converts text into vectors (lists of numbers) so your RAG system can do semantic search.

The chat model (OLLAMA_MODEL) writes the final answer.
The embedding model (OLLAMA_EMBED_MODEL) finds the relevant context first.

RAG quality depends heavily on this retrieval step. If retrieval is weak, the final answer is weak.
=================================

Why You Need It

RAG has 2 different jobs:

Retrieval job
Find the most relevant chunks from your knowledge base.
Needs embeddings + vector similarity.
Generation job
Use those chunks to answer naturally.
Needs a chat/generation model.
================================
If you only use a chat model without embeddings, you are not really doing semantic retrieval from your own indexed docs.
===============================

current flow is:

Index docs:
Text chunk -> embedding model -> vectors
Vectors stored in ChromaDB
Ask question:
Question -> same embedding model -> query vector
ChromaDB returns nearest chunks
Chat model gets prompt with those chunks and generates answer
Relevant code path:

Index: main.py:82
Ask/query: main.py:106
Ollama embed call: main.py:57
Ollama chat call: main.py:144
======================================
Critical Rule

Use the same embedding model for:

indexing
querying
If you index with model A and query with model B, vector spaces differ and retrieval quality drops badly.
=====================================

Practical Example 1: See Embeddings Directly

Run inside your stack:
docker compose exec ollama curl -sS http://localhost:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","input":["cat sits on mat","feline on rug","quantum mechanics"]}'

  You will get numeric vectors.
The first two texts should be semantically closer than either is to quantum mechanics.
=====================================

Practical Example 2: End-to-End RAG Test

Index:

docker compose exec llm-server curl -sS -X POST http://localhost:8081/api/rag/index
-H "Content-Type: application/json"
-d '{"collection":"demo","documents":["Redis is an in-memory data store.","PostgreSQL is a relational database."]}'

Ask:

docker compose exec llm-server curl -sS -X POST http://localhost:8081/api/rag/ask
-H "Content-Type: application/json"
-d '{"collection":"demo","question":"Which one is relational?","top_k":2}'

Expected behavior:

contexts should include PostgreSQL chunk
answer should mention PostgreSQL as relational
Practical Example 3: Show Why Embedding Choice Matters

Try a domain-specific corpus (for example, coding docs).
Run the same queries with:

nomic-embed-text
another embedding model you pull in Ollama
Compare:

retrieved contexts relevance
answer groundedness
hallucination rate
Simple evaluation method:

Build 20 question-answer pairs where true answer is in indexed docs.
Measure hit rate: context contains needed fact in top_k.
Then measure final answer accuracy.
If hit rate is low, improve embedding model/chunking first, not prompt wording.

How To Choose an Embedding Model

Start with nomic-embed-text when you want:

solid general retrieval
simple local setup
good speed/quality balance
Consider alternatives when you need:

multilingual retrieval
better performance on code/legal/biomedical text
lower memory or faster indexing constraints
Decision checklist:

Language coverage needed?
Domain-specific jargon?
Latency budget?
Hardware limits?
Corpus size growth over time?
Common Mistakes

Not pulling embedding model in advance
fixed in your init script now
Index/query model mismatch
causes poor retrieval
Chunking too large
noisy contexts, lower precision
top_k too high
too much irrelevant context in prompt
Thinking chat model quality alone fixes RAG
retrieval quality is usually the bottleneck
Your Repo-Specific Bottom Line

OLLAMA_MODEL is for answer generation.
OLLAMA_EMBED_MODEL is required for semantic retrieval.
You need both for true RAG.
Your current default in .env:13 is a good baseline: nomic-embed-text.
If you want, next I can give you a small 30-minute evaluation lab in your repo: 10 test docs, 10 queries, and a tiny scoring sheet to compare embedding models objectively.


