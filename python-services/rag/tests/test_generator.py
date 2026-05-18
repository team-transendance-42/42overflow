"""
Tests for generator.py — prompt construction and (optionally) Ollama generation.

test_build_prompt_*  — pure string logic, no services needed.
test_generate        — requires Ollama running (docker compose up -d).

Run offline: uv run pytest tests/test_generator.py -v -k "not test_generate"
Run all:     uv run pytest tests/test_generator.py -v  (needs Ollama)
"""
from generator import build_prompt, _extract_answer, _truncate

# ── fixtures ──────────────────────────────────────────────────────────────────

_FAKE_CONTEXTS = [
    {"id": "abc", "text": "Q: What is free()?\nA: Releases heap memory.", "rrf_score": 0.03},
    {"id": "def", "text": "Q: What is malloc()?\nA: Allocates heap memory.", "rrf_score": 0.02},
]

# ── _extract_answer ───────────────────────────────────────────────────────────


def test_extract_answer_standard_format():
    """Extracts the A: portion from standard 'Q: ...\nA: ...' format."""
    text = "Q: What is free()?\nA: Releases heap memory."
    result = _extract_answer(text)
    assert result == "Releases heap memory."


def test_extract_answer_strips_tags():
    """Tags appended for embedding signal must be stripped from the answer."""
    text = "Q: What is norminette?\nA: A style checker.\ntags: norminette c"
    result = _extract_answer(text)
    assert result == "A style checker."
    assert "tags:" not in result


def test_extract_answer_no_separator_falls_back():
    """
    If 'A: ' separator not found, return full text — don't crash.
    Edge case: malformed or non-standard doc stored in ChromaDB.
    """
    text = "some raw text without the expected format"
    result = _extract_answer(text)
    assert result == text


def test_extract_answer_empty_answer_falls_back():
    """
    If answer part is empty after split, fall back to full text.
    Edge case: doc stored as 'Q: question\nA: ' with empty answer.
    """
    text = "Q: What is X?\nA: "
    result = _extract_answer(text)
    # empty stripped answer → fallback to full text
    assert len(result) > 0

# ── _truncate ─────────────────────────────────────────────────────────────────


def test_truncate_long_text():
    """Text longer than max_chars is truncated and gets ellipsis."""
    long_text = "a" * 400
    result = _truncate(long_text, max_chars=300)
    assert len(result) <= 304   # 300 chars + "…" (1 char) + some slack
    assert result.endswith("…")


def test_truncate_short_text_unchanged():
    """Text shorter than max_chars is returned unchanged, no ellipsis."""
    short = "Short answer."
    assert _truncate(short, max_chars=300) == short
    assert "…" not in _truncate(short, max_chars=300)


def test_truncate_exactly_max_unchanged():
    """Text exactly at max_chars boundary is not truncated."""
    text = "x" * 300
    assert _truncate(text, max_chars=300) == text

# ── build_prompt ──────────────────────────────────────────────────────────────


def test_build_prompt_contains_answer_not_question():
    """
    The prompt must contain the answer text but NOT the Q: question lines.
    Theory: question part is retrieval metadata — redundant in the prompt since
    the user's own question is already present. Dropping it saves ~40% tokens.
    """
    prompt = build_prompt("how does memory work?", _FAKE_CONTEXTS)

    # Answer text must be present
    assert "Releases heap memory." in prompt
    assert "Allocates heap memory." in prompt

    # Question prefix must be stripped
    assert "Q: What is free()?" not in prompt
    assert "Q: What is malloc()?" not in prompt


def test_build_prompt_structure_intact():
    """All structural sections must still be present after the change."""
    prompt = build_prompt("how does memory work?", _FAKE_CONTEXTS)

    assert "=== CONTEXT ===" in prompt
    assert "=== QUESTION ===" in prompt
    assert "=== ANSWER ===" in prompt
    assert "how does memory work?" in prompt
    assert "[1]" in prompt
    assert "[2]" in prompt


def test_build_prompt_empty_contexts():
    """Empty context list → fallback message, no crash, structure intact."""
    prompt = build_prompt("anything?", [])
    assert "no context retrieved" in prompt
    assert "=== QUESTION ===" in prompt


def test_build_prompt_truncates_long_answer():
    """
    Answers longer than MAX_CONTEXT_CHARS are truncated in the prompt.
    Theory: shorter context = fewer tokens = faster per-token generation.
    """
    long_answer = "Very long answer. " * 50    # ~900 chars
    ctx = [{"id": "x", "text": f"Q: A question?\nA: {long_answer}", "rrf_score": 0.1}]
    prompt = build_prompt("question", ctx)

    # The full long answer must NOT appear verbatim
    assert long_answer not in prompt
    # But a truncated version must appear (ends with ellipsis)
    assert "…" in prompt


def test_build_prompt_malformed_context_no_crash():
    """
    A context dict without 'A: ' in text must not crash build_prompt.
    Falls back to full text for that block.
    """
    ctx = [{"id": "x", "text": "just some raw text no format", "rrf_score": 0.1}]
    prompt = build_prompt("question", ctx)
    assert "just some raw text no format" in prompt
    assert "=== ANSWER ===" in prompt


# ── tutor-style prompt tests (Task 2) ─────────────────────────────────────────


def test_build_prompt_tutor_style():
    """Prompt must instruct synthesis, not extraction."""
    contexts = [{"text": "Q: What is X?\nA: X is a thing.", "rrf_score": 0.1}]
    prompt = build_prompt("what is X", contexts)
    prompt_lower = prompt.lower()
    assert "tutor" in prompt_lower, "prompt should identify the model as a tutor"
    assert "explain" in prompt_lower, "prompt should tell the model to explain"
    assert "answer using only" not in prompt_lower, "old extract-style instruction must be removed"


def test_build_prompt_no_context():
    """Empty contexts still produce a structurally valid prompt."""
    prompt = build_prompt("what is X", [])
    assert "no context" in prompt.lower()
    assert "=== QUESTION ===" in prompt
    assert "=== ANSWER ===" in prompt


def test_build_prompt_strips_question_prefix():
    """Answer-only extraction: Q: prefix is dropped from context blocks."""
    contexts = [{"text": "Q: What is X?\nA: X is a wonderful thing.", "rrf_score": 0.1}]
    prompt = build_prompt("what is X", contexts)
    assert "X is a wonderful thing." in prompt
    assert "[1]" in prompt
