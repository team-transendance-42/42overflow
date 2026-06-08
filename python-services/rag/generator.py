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

# Maximum characters kept per context block in the prompt.
# Theory: shorter context = fewer tokens = faster per-token generation.
# ~300 chars ≈ 75-100 tokens — enough to convey an answer, not enough to bloat.
MAX_CONTEXT_CHARS = 300


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


def _truncate(text: str, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    Truncate text to max_chars characters, appending '…' when cut.

    Theory: limits context tokens per retrieved block so the LLM prompt stays
    short and generation latency stays low (attention is quadratic in sequence
    length on CPU). The ellipsis signals to the LLM that the snippet is partial.

    Pros:
      - Predictable token budget per context block
      - Ellipsis gives the LLM a hint that more detail exists

    Edge cases:
      - text ≤ max_chars → returned unchanged, no ellipsis added
      - max_chars=0 → returns '…' (degenerate but won't crash)
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"


def build_prompt(question: str, contexts: list[dict]) -> str:
    """
    Assemble the RAG prompt from retrieved context docs.

    Instructs the LLM to explain as a tutor, not to extract sentences.
    Each context block is reduced to its answer-only snippet so the
    retrieved question prefix does not occupy tokens unnecessarily.
    Long snippets are truncated to MAX_CONTEXT_CHARS to keep the prompt
    short and generation fast on CPU.

    Pros:
      - Tutor framing → model synthesises and explains, not copy-pastes
      - Answer-only + truncation → ~50-70% fewer context tokens
      - Numbered blocks → easy to trace which doc drove the answer

    Cons:
      - Truncation may drop tail of very long answers (rare in 42 FAQ docs)

    Edge cases:
      - Empty contexts → fallback message, structure stays intact
      - Malformed doc (no 'A: ') → _extract_answer falls back to full text
    """
    if not contexts:
        context_str = "(no context retrieved)"
    else:
        blocks = [
            f"[{i + 1}] {_truncate(_extract_answer(c['text']))}"
            for i, c in enumerate(contexts)
        ]
        context_str = "\n\n".join(blocks)

    return (
        "You are a tutor for 42 school students.\n"
        "Using the context below as your source, explain the concept clearly\n"
        "and completely — as if the student asked you in person.\n"
        "Cover what it is, why it matters, and the key details.\n"
        "Synthesise naturally; do not copy sentences verbatim from the context.\n"
        "If the context does not contain enough to answer, say: "
        "\"I don't have enough context to answer this fully.\"\n"
        "Never say things like \"The community hasn't covered this\" or "
        "\"be the first to post\" — you are a tutor, not a forum.\n\n"
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

    answer = response.json()["message"]["content"].strip()

    # Small models sometimes ignore prompt instructions and emit forum-style
    # "no answer yet" placeholders learned from pretraining data.
    # Detect and replace rather than forward confusing output to the user.
    _HALLUCINATION_MARKERS = [
        "community hasn't covered",
        "be the first to post",
        "no one has answered",
        "this question has no answers",
    ]
    if any(m in answer.lower() for m in _HALLUCINATION_MARKERS):
        ctx_note = "with the available context" if contexts else "— no relevant context was found"
        return f"I don't have enough information to answer this fully {ctx_note}."

    return answer
