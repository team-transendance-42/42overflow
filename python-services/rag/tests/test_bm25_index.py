"""
Run: uv run python test_bm25_index.py
No services required — BM25 is pure in-memory math.

Note: BM25 scores are raw floats, not normalized to [0, 1].
The hybrid retriever uses only rank position (not score value) for RRF,
so absolute score magnitude doesn't matter here — only ordering does.
"""
from bm25_index import BM25Index


def test_keyword_scoring():
    idx = BM25Index()
    docs = [
        "Q: What is free()?\nA: Releases heap memory.",
        "Q: What is malloc()?\nA: Allocates heap memory.",
        "Q: What causes a segfault?\nA: Dereferencing a null pointer.",
    ]
    ids = ["free-1", "malloc-2", "seg-3"]
    idx.build(docs, ids)

    results = idx.search("heap memory allocation", n=3)
    assert len(results) > 0, "expected at least one result for 'heap memory allocation'"
    assert all("id" in r and "score" in r for r in results)

    result_ids = [r["id"] for r in results]
    assert "free-1" in result_ids or "malloc-2" in result_ids, \
        f"heap/malloc docs should rank highest, got: {result_ids}"
    assert "seg-3" not in result_ids[:1], \
        "segfault doc should not be the top result for a heap query"

    print(f"✓ keyword scoring: top hits for 'heap memory allocation': {result_ids}")


def test_exact_token_match():
    idx = BM25Index()
    idx.build(
        ["Q: What is a segfault?\nA: Null pointer dereference causes a segfault."],
        ["seg-1"],
    )
    results = idx.search("segfault")
    assert len(results) == 1, f"expected 1 result, got {len(results)}"
    assert results[0]["id"] == "seg-1"
    assert results[0]["score"] > 0
    print(f"✓ exact token match: 'segfault' → score={results[0]['score']:.3f}")


def test_no_match_returns_empty():
    idx = BM25Index()
    idx.build(["Q: What is X?\nA: X is Y."], ["id-1"])
    results = idx.search("zzz nonexistent gibberish xyz")
    assert results == [], f"expected [], got {results}"
    print("✓ no match: unrelated query returns [] (zero-score docs filtered out)")


def test_unbuilt_index_search_is_safe():
    idx = BM25Index()
    results = idx.search("anything at all")
    assert results == [], f"expected [], got {results}"
    print("✓ unbuilt index: search() returns [] safely without crashing")


def test_results_ordered_by_score():
    idx = BM25Index()
    idx.build(
        [
            "Q: What is a pointer?\nA: An address in memory.",
            "Q: What is a null pointer?\nA: A pointer that points to address zero, null pointer dereference crashes.",
        ],
        ["ptr-1", "null-ptr-2"],
    )
    results = idx.search("null pointer")
    assert len(results) >= 1
    if len(results) > 1:
        assert results[0]["score"] >= results[1]["score"], \
            "results must be sorted by descending score"
    print(f"✓ ordering: results sorted by score desc — top: {results[0]['id']} ({results[0]['score']:.3f})")


if __name__ == "__main__":
    test_keyword_scoring()
    test_exact_token_match()
    test_no_match_returns_empty()
    test_unbuilt_index_search_is_safe()
    test_results_ordered_by_score()
    print("\nAll BM25 tests passed.")
