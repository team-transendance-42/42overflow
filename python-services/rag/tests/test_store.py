"""
Run:  docker exec -it 42overflow-python-rag-1 bash // enter container
      uv run python -m tests.test_store
Requires: ChromaDB running (docker compose up -d)
Uses collection 'qa_pairs_test' — safe to run anytime.
"""
from store import ensure_collection, get_existing_hashes, upsert

_TEST = "qa_pairs_test"


def test_upsert_and_retrieve():
    ensure_collection(_TEST)
    upsert(
        ids=["id-1", "id-2"],
        documents=["Q: What is free()?\nA: Releases heap memory.", "Q: What is malloc()?\nA: Allocates heap memory."],
        embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        metadatas=[{"doc_hash": "hash-a", "topic": "c"}, {"doc_hash": "hash-b", "topic": "c"}],
        name=_TEST,
    )
    hashes = get_existing_hashes(["id-1", "id-2"], name=_TEST)
    assert hashes["id-1"] == "hash-a"
    assert hashes["id-2"] == "hash-b"
    print("✓ upsert_and_retrieve: 2 docs stored, hashes retrievable")


def test_get_hashes_only_returns_existing():
    ensure_collection(_TEST)
    hashes = get_existing_hashes(["id-1", "id-MISSING"], name=_TEST)
    assert "id-1" in hashes, "existing ID must be returned"
    assert "id-MISSING" not in hashes, "missing ID must not appear"
    print("✓ get_hashes: missing IDs are silently absent")


def test_upsert_overwrites_on_second_run():
    ensure_collection(_TEST)
    upsert(
        ids=["id-1"],
        documents=["Q: What is free()?\nA: Updated answer."],
        embeddings=[[0.9, 0.8, 0.7]],
        metadatas=[{"doc_hash": "hash-updated", "topic": "c"}],
        name=_TEST,
    )
    hashes = get_existing_hashes(["id-1"], name=_TEST)
    assert hashes["id-1"] == "hash-updated", "second upsert must overwrite hash"
    print("✓ upsert overwrites: hash updated correctly on re-upsert")


if __name__ == "__main__":
    test_upsert_and_retrieve()
    test_get_hashes_only_returns_existing()
    test_upsert_overwrites_on_second_run()
    print("\nAll store tests passed.")
