"""
Run: uv run python -m tests.test_router
Requires: full stack running (docker compose up -d).
Hits the live /rag/ask endpoint via HTTP — tests the full pipeline:
hybrid_search → generate → FastAPI response.
"""
import httpx

BASE = "http://localhost:8090"


def test_ask_returns_answer():
    resp = httpx.post(f"{BASE}/rag/ask", json={"question": "what is a segfault?"}, timeout=300)

    assert resp.status_code == 200, f"expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    assert "answer" in data, "response missing 'answer'"
    assert len(data["answer"]) > 0, "answer must not be empty"

    print(f"\n── /rag/ask response ───────────────────────────────────")
    print(f"  question : 'what is a segfault?'")
    print(f"  answer   : {data['answer'][:200]!r}")
    print("✓ /rag/ask: valid response with answer")


def test_ask_empty_question_is_rejected():
    resp = httpx.post(f"{BASE}/rag/ask", json={"question": "   "}, timeout=10)
    assert resp.status_code == 422, f"expected 422 for empty question, got {resp.status_code}"
    print("✓ /rag/ask: empty question rejected with 422")


def test_healthz_still_works():
    resp = httpx.get(f"{BASE}/healthz", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["qa_count"] > 0, "qa_count should be > 0 after startup"
    print(f"✓ /healthz: ok, qa_count={data['qa_count']}")


if __name__ == "__main__":
    test_healthz_still_works()
    test_ask_empty_question_is_rejected()
    test_ask_returns_answer()
    print("\nAll router tests passed.")
