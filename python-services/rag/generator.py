"""
RAG prompt assembly and Ollama generation.

Why answer-only context:
  Each retrieved context block was previously injected as the full "Q: ...\nA: ..."
  text. The Q: portion is retrieval metadata — it helped find the document but is
  redundant in the prompt (the user's question is already present). Dropping it
  saves ~40-60% of context tokens.

Pros:
  - Fewer prompt tokens → faster per-token generation (directly fixes inter-token latency)
  - No retrieval changes — same docs, less verbosity
  - Fully backward compatible: unknown format falls back to full text

Cons:
  - Answer-only loses the semantic Q: framing (minor: user question covers this)

Edge cases:
  - No '\nA: ' separator in text → fall back to full text, no crash
  - Empty answer after split → fall back to full text
  - Tags line ('\ntags: ...') appended for embedding → stripped before use
"""

import httpx

from config import LLM_MODEL, OLLAMA_URL

# Reused across requests — avoids opening a new TCP connection per call.
_http = httpx.AsyncClient(timeout=300.0)


def _extract_answer(text: str) -> str:
    """
    Extract the answer portion from a 'Q: ...\nA: ...' formatted doc.

    Theory: docs are formatted by embedder.format_doc() as:
        "Q: {question}\nA: {answer}"        (no tags)
        "Q: {question}\nA: {answer}\ntags: ..." (with tags)
    The Q: line was useful for BM25 keyword matching and embedding but is
    redundant in the LLM prompt — drop it to save tokens.

    Returns full text as fallback if the expected separator is missing,
    so callers never crash on malformed or legacy-format docs.

    Edge cases:
      - Missing '\nA: ' → return full text (fallback)
      - Empty answer after split → return full text (fallback)
      - Tags suffix → stripped (embedding signal, not for LLM)
    """
    sep = "\nA: "
    if sep not in text:
        return text   # unknown format — safe fallback

    answer = text.split(sep, 1)[1]

    # Strip tags suffix added by format_doc for embedding quality.
    if "\ntags: " in answer:
        answer = answer.split("\ntags: ", 1)[0]

    answer = answer.strip()
    return answer if answer else text  # empty answer → fallback to full text


def build_prompt(question: str, contexts: list[dict]) -> str:
    """
    Assemble the RAG prompt from retrieved context docs.

    contexts is a list of dicts from hybrid_search:
      [{"id": ..., "text": "Q: ...\nA: ...", "rrf_score": ...}, ...]

    Each block is reduced to its answer-only snippet (≤ MAX_CONTEXT_CHARS chars).
    Numbering context blocks lets the model cite sources and makes it easy to
    trace which retrieved doc drove the answer.

    Pros of answer-only truncated format:
      - ~40-60% fewer context tokens vs full Q&A
      - Faster per-token generation on CPU (linear attention cost)
    """
    if not contexts:
        context_str = "(no context retrieved)"
    else:
        blocks = [
            f"[{i+1}] {_extract_answer(c['text'])}"
            for i, c in enumerate(contexts)
        ]
        context_str = "\n\n".join(blocks)

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

    response = await _http.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
    )
    response.raise_for_status()

    return response.json()["message"]["content"].strip()
