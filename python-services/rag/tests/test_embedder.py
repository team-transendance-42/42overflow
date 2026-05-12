"""
Run: uv run python test_embedder.py
Requires: Ollama running (docker compose up -d)
"""
import asyncio
from embedder import embed_texts, format_doc, make_doc_hash, make_doc_id


def test_helpers():
    assert format_doc("What is X?", "X is Y.") == "Q: What is X?\nA: X is Y."

    assert make_doc_id("What is X?") == make_doc_id("What is X?"), "ID must be stable"
    assert make_doc_id("What is X?") != make_doc_id("What is Y?"), "different Q → different ID"

    assert make_doc_hash("Q", "A") == make_doc_hash("Q", "A"), "hash must be stable"
    assert make_doc_hash("Q", "A1") != make_doc_hash("Q", "A2"), "hash must change with answer"
    assert make_doc_hash("Q1", "A") != make_doc_hash("Q2", "A"), "hash must change with question"

    print("✓ helpers: format, ID stability/uniqueness, hash sensitivity")


def test_embed_texts():
    result = asyncio.run(embed_texts(["hello world", "free the pointer"]))

    assert isinstance(result, list), "result must be a list"
    assert len(result) == 2, f"expected 2 vectors, got {len(result)}"
    assert len(result[0]) > 0, "vector must not be empty"
    assert len(result[0]) == len(result[1]), "all vectors must be same length"
    assert all(isinstance(v, float) for v in result[0]), "vector values must be floats"

    print(f"✓ embed_texts: 2 vectors of length {len(result[0])}")


if __name__ == "__main__":
    test_helpers()
    test_embed_texts()
    print("\nAll embedder tests passed.")
