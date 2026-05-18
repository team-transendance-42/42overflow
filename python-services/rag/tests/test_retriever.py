"""
Retriever integration tests — run fully offline, no ChromaDB or Docker needed.

NumpyIndex replaces ChromaDB for dense search, so these tests work on the
host with: uv run pytest tests/test_retriever.py -v

These tests verify the full retrieval pipeline end to end:
  embed → NumpyIndex cosine search → BM25 → RRF merge → topic detection.
"""
import asyncio

from bm25_index import BM25Index
from detector import build_topic_centroids
from embedder import embed_texts, format_doc, make_doc_id
from numpy_index import NumpyIndex
from retriever import hybrid_search
from seed import load_seed


def _build_test_fixtures(with_centroids: bool = False):
    """
    Build all in-memory fixtures from seed — mirrors what lifespan() does.

    Always computes embeddings (needed for NumpyIndex).
    with_centroids=True: also builds topic centroids for topic-aware retrieval.
    with_centroids=False: centroids={} → full corpus search, no topic filter.

    Edge case: fastembed loads the model on first call (~2s), cached thereafter.
    """
    pairs = load_seed()
    all_texts = [format_doc(p["question"], p["answer"], p.get("tags", [])) for p in pairs]
    all_ids = [make_doc_id(p["question"]) for p in pairs]
    all_topics = [p.get("topic", "unknown") for p in pairs]

    id_to_text = dict(zip(all_ids, all_texts))
    id_to_topic = dict(zip(all_ids, all_topics))

    bm25 = BM25Index()
    bm25.build(documents=all_texts, ids=all_ids, topics=all_topics)

    # Always embed — NumpyIndex needs real vectors for meaningful dense search.
    embeddings = asyncio.run(embed_texts(all_texts))

    numpy_idx = NumpyIndex()
    numpy_idx.build(
        ids=all_ids,
        embeddings=embeddings,
        topics=all_topics,
        documents=all_texts,
    )

    centroids = build_topic_centroids(pairs, embeddings) if with_centroids else {}

    return bm25, numpy_idx, id_to_text, id_to_topic, centroids


def test_result_shape():
    """hybrid_search returns a list of dicts with the expected keys."""
    bm25, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures()

    results = asyncio.run(hybrid_search(
        "what is a segfault", bm25, numpy_idx, id_to_text, id_to_topic, centroids, top_k=3
    ))

    assert isinstance(results, list), "result must be a list"
    assert len(results) <= 3, f"expected at most 3 results, got {len(results)}"
    assert len(results) > 0, "expected at least 1 result"

    for r in results:
        assert "id" in r, f"missing 'id' key: {r}"
        assert "text" in r, f"missing 'text' key: {r}"
        assert "rrf_score" in r, f"missing 'rrf_score' key: {r}"
        assert "topic" in r, f"missing 'topic' key: {r}"
        assert r["text"].startswith("Q:"), f"text should start with 'Q:': {r['text'][:40]}"
        assert r["rrf_score"] > 0, f"rrf_score must be positive: {r['rrf_score']}"

    print(f"✓ result shape: {len(results)} results, all keys present")


def test_results_sorted_by_rrf_score():
    """Results must be sorted by descending rrf_score."""
    bm25, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures()

    results = asyncio.run(hybrid_search(
        "memory allocation deadlock", bm25, numpy_idx, id_to_text, id_to_topic, centroids, top_k=5
    ))
    scores = [r["rrf_score"] for r in results]

    assert scores == sorted(scores, reverse=True), \
        f"results not sorted by rrf_score: {scores}"
    print(f"✓ ordering: scores descending {[round(s, 4) for s in scores]}")


def test_relevant_doc_in_top_results():
    """A specific keyword query should surface a relevant doc in top-3."""
    bm25, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures()

    results = asyncio.run(hybrid_search(
        "EDF scheduling deadline coder dongle",
        bm25, numpy_idx, id_to_text, id_to_topic, centroids, top_k=3,
    ))
    texts = [r["text"].lower() for r in results]

    assert any("edf" in t or "deadline" in t or "coder" in t or "dongle" in t for t in texts), \
        f"expected a relevant doc in top-3, got: {[r['text'][:60] for r in results]}"
    print(f"✓ relevance: top result: {results[0]['text'][:80]!r}")


def test_dense_only_fallback():
    """When BM25 returns no matches (empty index), NumpyIndex dense results come through."""
    _, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures()

    empty_bm25 = BM25Index()
    results = asyncio.run(hybrid_search(
        "what is malloc", empty_bm25, numpy_idx, id_to_text, id_to_topic, centroids, top_k=3
    ))

    assert len(results) > 0, "dense-only fallback must still return results from NumpyIndex"
    assert all(r["rrf_score"] > 0 for r in results)
    print(f"✓ dense-only fallback: {len(results)} results from NumpyIndex alone")


def test_topic_aware_retrieval_codexion():
    """A codexion-specific query should return mostly codexion docs with centroids."""
    bm25, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures(with_centroids=True)

    results = asyncio.run(hybrid_search(
        "EDF deadline scheduling dongle coder burnout pthread",
        bm25, numpy_idx, id_to_text, id_to_topic, centroids,
        top_k=5,
    ))

    assert len(results) > 0
    codexion_hits = sum(1 for r in results if id_to_topic.get(r["id"]) == "codexion")
    assert codexion_hits >= 3, (
        f"expected ≥3 codexion results for a codexion query, got {codexion_hits}. "
        f"Topics: {[id_to_topic.get(r['id']) for r in results]}"
    )
    print(f"✓ topic-aware: {codexion_hits}/5 results are codexion")


def test_fallback_when_no_topic_detected():
    """A generic query should return results without locking to one topic."""
    bm25, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures(with_centroids=True)

    results = asyncio.run(hybrid_search(
        "error handling graceful exit",
        bm25, numpy_idx, id_to_text, id_to_topic, centroids,
        top_k=5,
    ))

    assert len(results) > 0, "fallback must still return results"
    print(f"✓ fallback: topics returned: {[id_to_topic.get(r['id']) for r in results]}")


def _build_topic_intro_ids() -> dict[str, str]:
    """Build {topic: intro_doc_id} from seed — mirrors what main.py will do."""
    pairs = load_seed()
    return {
        p["topic"]: make_doc_id(p["question"])
        for p in pairs
        if "intro" in p.get("tags", [])
    }


def test_intro_pinned_when_not_in_top_results():
    """Intro doc at position 0 when topic detected and intro not naturally in top-k."""
    bm25, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures(
        with_centroids=True
    )
    topic_intro_ids = _build_topic_intro_ids()

    # Highly specific query unlikely to retrieve the codexion intro overview doc.
    results = asyncio.run(hybrid_search(
        "EDF deadline heap extract min priority recompile dongle coder burnout",
        bm25, numpy_idx, id_to_text, id_to_topic, centroids,
        topic_intro_ids=topic_intro_ids,
        top_k=4,
    ))

    codexion_intro_id = topic_intro_ids["codexion"]
    assert results[0]["id"] == codexion_intro_id, (
        f"intro doc should be pinned at position 0, "
        f"got: {results[0].get('text', '')[:80]!r}"
    )
    print("✓ intro pinning: first result is intro doc")


def test_intro_not_duplicated_when_already_retrieved():
    """When intro naturally ranks in top-k, it appears exactly once."""
    bm25, numpy_idx, id_to_text, id_to_topic, centroids = _build_test_fixtures(
        with_centroids=True
    )
    topic_intro_ids = _build_topic_intro_ids()

    results = asyncio.run(hybrid_search(
        "what is codexion dining philosophers overview intro",
        bm25, numpy_idx, id_to_text, id_to_topic, centroids,
        topic_intro_ids=topic_intro_ids,
        top_k=4,
    ))

    ids = [r["id"] for r in results]
    assert len(ids) == len(set(ids)), (
        f"intro doc must not appear twice, got ids: {ids}"
    )
    print(f"✓ no duplicate: {len(ids)} unique results")


def test_no_pinning_when_no_topic_detected():
    """Without centroids (no topic detection), intro pinning is skipped — no crash."""
    bm25, numpy_idx, id_to_text, id_to_topic, _ = _build_test_fixtures(with_centroids=False)
    topic_intro_ids = _build_topic_intro_ids()

    results = asyncio.run(hybrid_search(
        "EDF deadline heap extract min",
        bm25, numpy_idx, id_to_text, id_to_topic,
        {},  # empty centroids → no topic detection → no pinning
        topic_intro_ids=topic_intro_ids,
        top_k=4,
    ))

    assert len(results) > 0, "should still return results when pinning is skipped"
    print(f"✓ no-topic fallback: {len(results)} results, no crash")


if __name__ == "__main__":
    test_result_shape()
    test_results_sorted_by_rrf_score()
    test_relevant_doc_in_top_results()
    test_dense_only_fallback()
    test_topic_aware_retrieval_codexion()
    test_fallback_when_no_topic_detected()
    test_intro_pinned_when_not_in_top_results()
    test_intro_not_duplicated_when_already_retrieved()
    test_no_pinning_when_no_topic_detected()
    print("\nAll retriever tests passed.")
