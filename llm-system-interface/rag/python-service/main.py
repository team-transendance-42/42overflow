import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="rag-python-service")


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value.rstrip("/")


CHROMA_URL = _env("CHROMA_URL", "http://chromadb:8000")
OLLAMA_URL = _env("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
DEFAULT_COLLECTION = "my_rag_collection"


class RagIndexRequest(BaseModel):
    collection: str | None = None
    documents: list[str]


class RagAskRequest(BaseModel):
    collection: str | None = None
    question: str
    top_k: int = Field(default=3, ge=1, le=20)


def _collection_name(name: str | None) -> str:
    if not name:
        return DEFAULT_COLLECTION
    trimmed = name.strip()
    return trimmed if trimmed else DEFAULT_COLLECTION


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.is_error:
        raise HTTPException(status_code=502, detail=resp.text)


async def _ensure_collection(client: httpx.AsyncClient, collection: str) -> None:
    payload: dict[str, Any] = {
        "name": collection,
        "get_or_create": True,
    }
    resp = await client.post(f"{CHROMA_URL}/api/v1/collections", json=payload)
    _raise_for_status(resp)


async def _embed_texts(client: httpx.AsyncClient, texts: list[str]) -> list[list[float]]:
    resp = await client.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": OLLAMA_EMBED_MODEL, "input": texts},
    )
    _raise_for_status(resp)
    data = resp.json()

    embeddings = data.get("embeddings")
    if isinstance(embeddings, list) and embeddings:
        return embeddings

    embedding = data.get("embedding")
    if isinstance(embedding, list) and embedding:
        return [embedding]

    raise HTTPException(status_code=502, detail="empty embeddings response")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/rag/index")
async def rag_index(req: RagIndexRequest) -> dict[str, Any]:
    documents = [doc.strip() for doc in req.documents if doc and doc.strip()]
    if not documents:
        raise HTTPException(status_code=400, detail="documents are required")

    collection = _collection_name(req.collection)

    async with httpx.AsyncClient(timeout=60.0) as client:
        await _ensure_collection(client, collection)

        embeddings = await _embed_texts(client, documents)
        if len(embeddings) != len(documents):
            raise HTTPException(status_code=502, detail="embedding count mismatch")

        ids = [f"doc-{i + 1}" for i in range(len(documents))]
        payload = {
            "ids": ids,
            "documents": documents,
            "embeddings": embeddings,
        }

        resp = await client.post(f"{CHROMA_URL}/api/v1/collections/{collection}/upsert", json=payload)
        _raise_for_status(resp)

    return {"ok": True, "indexed": len(documents), "collection": collection}


@app.post("/rag/ask")
async def rag_ask(req: RagAskRequest) -> dict[str, Any]:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    collection = _collection_name(req.collection)

    async with httpx.AsyncClient(timeout=60.0) as client:
        query_embedding = await _embed_texts(client, [question])

        query_payload: dict[str, Any] = {
            "query_embeddings": query_embedding,
            "n_results": req.top_k,
        }
        query_resp = await client.post(
            f"{CHROMA_URL}/api/v1/collections/{collection}/query",
            json=query_payload,
        )
        _raise_for_status(query_resp)

        documents = query_resp.json().get("documents", [])
        contexts = documents[0] if documents else []

        context_text = "No context found."
        if contexts:
            context_text = "\n---\n".join(contexts)

        prompt = (
            "Use the context below to answer. If context is missing, say you are unsure briefly.\n\n"
            f"Context:\n{context_text}\n\nQuestion:\n{question}"
        )
        chat_payload = {
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        }
        chat_resp = await client.post(f"{OLLAMA_URL}/api/chat", json=chat_payload)
        _raise_for_status(chat_resp)

        answer = chat_resp.json().get("message", {}).get("content", "").strip()
        if not answer:
            raise HTTPException(status_code=502, detail="empty model answer")

    return {"answer": answer, "contexts": contexts}