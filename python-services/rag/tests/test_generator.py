"""
Run: uv run python -m tests.test_generator
test_build_prompt — no services needed (pure string logic).
test_generate     — requires Ollama running (docker compose up -d).
"""
import asyncio

from generator import build_prompt, generate

_FAKE_CONTEXTS = [
    {"id": "abc", "text": "Q: What is free()?\nA: Releases heap memory.", "rrf_score": 0.03},
    {"id": "def", "text": "Q: What is malloc()?\nA: Allocates heap memory.", "rrf_score": 0.02},
]


def test_build_prompt():
    prompt = build_prompt("how does memory work?", _FAKE_CONTEXTS)

    assert "=== CONTEXT ===" in prompt
    assert "=== QUESTION ===" in prompt
    assert "=== ANSWER ===" in prompt
    assert "how does memory work?" in prompt
    assert "[1]" in prompt and "[2]" in prompt
    assert "Q: What is free()?" in prompt
    assert "Q: What is malloc()?" in prompt
    print("✓ build_prompt: all sections and context blocks present")

    # empty contexts → fallback message, not a crash
    prompt_empty = build_prompt("anything?", [])
    assert "no context retrieved" in prompt_empty
    print("✓ build_prompt: empty contexts → fallback message, no crash")


def test_generate():
    answer = asyncio.run(
        generate("What does free() do in C?", _FAKE_CONTEXTS) # start asynchronous test, get answer string back
    )

    assert isinstance(answer, str), "answer must be a string"
    assert len(answer) > 0, "answer must not be empty"
    print(f"\n── generate output ─────────────────────────────────────")
    print(f"  question : 'What does free() do in C?'")
    print(f"  contexts : {[c['text'][:40] for c in _FAKE_CONTEXTS]}")
    print(f"  answer   : {answer[:200]}")
    print(f"  length   : {len(answer)} chars")
    print("✓ generate: got non-empty answer from Ollama")


if __name__ == "__main__":
    test_build_prompt()
    print()
    test_generate()
    print("\nAll generator tests passed.")
