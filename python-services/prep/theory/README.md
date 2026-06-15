# RAG Module (Go + Chroma + Ollama)

This folder documents the Go-first RAG flow used by `llm-server`.

## Endpoints

- `POST /api/rag/index`
  - Body:
    - `collection` (string, optional, default `my_rag_collection`)
    - `documents` (array of strings, required)
  - Behavior:
    - Ensures the Chroma collection exists.
    - Builds embeddings via Ollama embed API.
    - Upserts docs into Chroma.

- `POST /api/rag/ask`
  - Body:
    - `collection` (string, optional, default `my_rag_collection`)
    - `question` (string, required)
    - `top_k` (int, optional, default `3`)
  - Behavior:
    - Embeds the question.
    - Queries Chroma for top matches.
    - Builds grounded prompt and asks Ollama.
    - Returns JSON with `answer` and `contexts`.

## Required Environment Variables

- `CHROMA_URL` (default: `http://chromadb:8000`)
- `OLLAMA_URL` (default: `http://ollama:11434`)
- `OLLAMA_MODEL` (default: `gemma4:4b`)
- `OLLAMA_EMBED_MODEL` (default: `nomic-embed-text`)

## Why no Python SDK

This project is Go-first. Using Chroma over HTTP keeps deployment simple and avoids managing a separate Python runtime just for ingestion/query.
