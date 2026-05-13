"""
Run: uv run python test_retriever.py
Requires: Ollama + ChromaDB running (docker compose up -d).
Uses the production 'qa_pairs' collection — must be synced first.

These are integration tests: they verify the full retrieval pipeline
(embed → vector search → BM25 → RRF) works end to end with real services.
"""
import asyncio

from bm25_index import BM25Index
from embedder   import embed_texts, format_doc, make_doc_id
from retriever  import hybrid_search
from seed       import load_seed


def _build_test_fixtures():
    """Build BM25 index and id_to_text from seed — same as startup does."""
    pairs = load_seed()
    id_to_text = {
        make_doc_id(p["question"]): format_doc(p["question"], p["answer"])
        for p in pairs
    }
    bm25 = BM25Index()
    bm25.build(
        documents=list(id_to_text.values()),
        ids=list(id_to_text.keys()),
    )
    return bm25, id_to_text


def test_result_shape():
    """hybrid_search returns a list of dicts with the expected keys."""
    bm25, id_to_text = _build_test_fixtures()

    results = asyncio.run(hybrid_search("what is a segfault", bm25, id_to_text, top_k=3))

    assert isinstance(results, list), "result must be a list"
    assert len(results) <= 3, f"expected at most 3 results, got {len(results)}"
    assert len(results) > 0, "expected at least 1 result"

    for r in results:
        assert "id"        in r, f"missing 'id' key: {r}"
        assert "text"      in r, f"missing 'text' key: {r}"
        assert "rrf_score" in r, f"missing 'rrf_score' key: {r}"
        assert r["text"].startswith("Q:"), f"text should start with 'Q:': {r['text'][:40]}"
        assert r["rrf_score"] > 0, f"rrf_score must be positive: {r['rrf_score']}"

    print(f"✓ result shape: {len(results)} results, all keys present")


def test_results_sorted_by_rrf_score():
    """Results must be sorted by descending rrf_score."""
    bm25, id_to_text = _build_test_fixtures()

    results = asyncio.run(hybrid_search("memory leak pointer", bm25, id_to_text, top_k=5))
    scores = [r["rrf_score"] for r in results]

    assert scores == sorted(scores, reverse=True), \
        f"results not sorted by rrf_score: {scores}"
    print(f"✓ ordering: scores descending {[round(s,4) for s in scores]}")


def test_relevant_doc_in_top_results():
    """A specific keyword query should surface the relevant doc in top-3."""
    bm25, id_to_text = _build_test_fixtures()

    # Query about segfault — should retrieve the double-free or null-pointer doc
    results = asyncio.run(hybrid_search("segfault null pointer", bm25, id_to_text, top_k=3))
    texts = [r["text"].lower() for r in results]

    assert any("segfault" in t or "null" in t or "pointer" in t for t in texts), \
        f"expected a relevant doc in top-3, got: {[r['text'][:60] for r in results]}"
    print(f"✓ relevance: top result: {results[0]['text'][:80]!r}")


def test_dense_only_fallback():
    """When BM25 returns no matches (empty index), dense results still come through."""
    _, id_to_text = _build_test_fixtures()

    # Use an empty (unbuilt) BM25 index — search() returns []
    empty_bm25 = BM25Index()

    results = asyncio.run(hybrid_search("what is malloc", empty_bm25, id_to_text, top_k=3))

    assert len(results) > 0, "dense-only fallback must still return results"
    assert all(r["rrf_score"] > 0 for r in results)
    print(f"✓ dense-only fallback: {len(results)} results from ChromaDB alone")


if __name__ == "__main__":
    test_result_shape()
    test_results_sorted_by_rrf_score()
    test_relevant_doc_in_top_results()
    test_dense_only_fallback()
    print("\nAll retriever tests passed.")
