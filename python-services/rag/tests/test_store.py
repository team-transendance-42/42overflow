"""
Run:  docker exec -it 42overflow-python-rag-1 bash // enter container
      uv run python -m tests.test_store
Requires: ChromaDB running (docker compose up -d)
Uses collection 'qa_pairs_test' for write tests — safe to run anytime.
test_query_dense also requires Ollama running and 'qa_pairs' synced.
"""
import asyncio

import pytest
from unittest.mock import patch, MagicMock

from embedder import embed_texts, format_doc, make_doc_id
from seed     import load_seed
from store    import ensure_collection, get_existing_hashes, query_dense, upsert

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


def test_ensure_collection_chroma_down():
    with patch("store._client") as mock_client_fn:
        mock_client_fn.return_value.get_or_create_collection.side_effect = Exception(
            "Connection refused"
        )
        with pytest.raises(RuntimeError, match="Could not connect to ChromaDB"):
            ensure_collection()


def test_get_existing_hashes_chroma_down():
    with patch("store._client") as mock_client_fn:
        mock_client_fn.return_value.get_or_create_collection.side_effect = Exception(
            "Connection refused"
        )
        with pytest.raises(RuntimeError, match="Could not connect to ChromaDB"):
            get_existing_hashes(["id-1"])


def test_upsert_chroma_down():
    with patch("store._client") as mock_client_fn:
        mock_client_fn.return_value.get_or_create_collection.side_effect = Exception(
            "Connection refused"
        )
        with pytest.raises(RuntimeError, match="Could not connect to ChromaDB"):
            upsert(
                ids=["id-1"],
                documents=["doc"],
                embeddings=[[0.1, 0.2]],
                metadatas=[{"doc_hash": "h"}],
            )


def test_query_dense():
    """
    Sanity-check query_dense using data already in ChromaDB.

    Strategy: use col.get(limit=1) to pull one stored doc + its embedding
    directly from ChromaDB, then pass that embedding to query_dense.
    The same doc MUST come back as top-1 — a vector is always its own
    nearest neighbour.

    No Ollama, no seed loading. Pure ChromaDB round-trip.
    Requires: 'qa_pairs' synced (docker compose up -d).
    """
    import chromadb
    from urllib.parse import urlparse
    from config import CHROMA_URL

    # grab one stored doc directly via ChromaDB's built-in collection API
    parsed = urlparse(CHROMA_URL)
    col    = chromadb.HttpClient(host=parsed.hostname, port=parsed.port) \
                     .get_or_create_collection("qa_pairs")

    raw = col.get(limit=1, include=["embeddings", "documents"])
    assert raw["ids"], "qa_pairs collection is empty — run docker compose up -d first"

    doc_id    = raw["ids"][0]
    embedding = raw["embeddings"][0]
    document  = raw["documents"][0]

    print("\n── query_dense input ───────────────────────────────────")
    print(f"  doc_id    : {doc_id}")
    print(f"  document  : {document[:80]!r}{'...' if len(document) > 80 else ''}")
    print(f"  embedding : [{embedding[0]:.4f}, {embedding[1]:.4f}, ...]  dim={len(embedding)}")

    # ── CALL ─────────────────────────────────────────────────────────
    results = query_dense(embedding, n=5)

    # ── OUTPUT ───────────────────────────────────────────────────────
    print("\n── query_dense output (top 5) ──────────────────────────")
    for i, r in enumerate(results):
        marker = "  ← expected" if r["id"] == doc_id else ""
        print(f"  [{i+1}] distance={r['distance']:.6f}  id={r['id'][:16]}...{marker}")
        print(f"       {r['document'][:70]!r}{'...' if len(r['document']) > 70 else ''}")

    # ── COMPARISON ───────────────────────────────────────────────────
    top_id = results[0]["id"]
    match  = top_id == doc_id
    print("\n── comparison ──────────────────────────────────────────")
    print(f"  expected top-1 id : {doc_id}")
    print(f"  got      top-1 id : {top_id}")
    print(f"  top-1 distance    : {results[0]['distance']:.6f}  (0.0 = exact match)")
    print(f"  result            : {'✓ match' if match else '✗ mismatch'}")

    assert len(results) > 0, "query_dense returned no results"
    assert match, (
        f"A doc's own embedding must return itself as top-1.\n"
        f"  expected: {doc_id}\n  got: {top_id}"
    )
    print("\n✓ query_dense: correct doc returned as top-1")


if __name__ == "__main__":
    test_upsert_and_retrieve()
    test_get_hashes_only_returns_existing()
    test_upsert_overwrites_on_second_run()
    print()
    test_query_dense()
    print("\nAll store tests passed.")
