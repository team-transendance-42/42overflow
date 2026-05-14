import httpx

from config import LLM_MODEL, OLLAMA_URL


def build_prompt(question: str, contexts: list[dict]) -> str:
    """
    Assemble the RAG prompt from retrieved context docs.

    contexts is a list of dicts from hybrid_search:
      [{"id": ..., "text": "Q: ...\nA: ...", "rrf_score": ...}, ...]

    Numbering context blocks lets the model cite sources and makes it
    easy to trace which retrieved doc drove the answer.
    """
    if not contexts:
        context_str = "(no context retrieved)"
    else:
        blocks = [f"[{i+1}] {c['text']}" for i, c in enumerate(contexts)]
        context_str = "\n\n".join(blocks) # after each block, add 2 newlines

    return (
        "You are a helpful assistant for 42 school students.\n"
        "Answer using ONLY the context provided below.\n"
        "If the context does not contain enough information, say so briefly.\n\n"
        f"=== CONTEXT ===\n{context_str}\n\n"
        f"=== QUESTION ===\n{question}\n\n"
        "=== ANSWER ==="
    )


async def generate(question: str, contexts: list[dict]) -> str:
    """
    Build a RAG prompt from contexts and send it to Ollama chat.

    Uses the non-streaming /api/chat endpoint — simpler for now.
    Returns the model's answer as a plain string.

    Raises httpx.HTTPError if Ollama is unreachable or returns an error.
    """
    prompt = build_prompt(question, contexts)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=300.0,
        )
        response.raise_for_status()

    return response.json()["message"]["content"].strip()
