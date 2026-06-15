"""
Tests for main.py startup logic.
Run: uv run python -m pytest tests/test_main.py -v
No live services needed — all external calls are mocked.
"""
import pytest
from unittest.mock import AsyncMock, patch


def test_merge_db_overwrites_seed():
    from main import _merge

    seed = [{"question": "Q1", "answer": "seed"}]
    db = [{"question": "Q1", "answer": "db"}, {"question": "Q2", "answer": "only-db"}]
    result = _merge(seed, db)

    by_q = {r["question"]: r for r in result}
    assert by_q["Q1"]["answer"] == "db"
    assert "Q2" in by_q


def test_merge_empty_db():
    from main import _merge

    seed = [{"question": "Q1", "answer": "seed"}]
    result = _merge(seed, [])
    assert len(result) == 1
    assert result[0]["answer"] == "seed"


def test_merge_bad_pair_raises():
    from main import _merge

    seed = [{"answer": "no question key here"}]  # missing "question"
    with pytest.raises(ValueError, match="missing 'question'"):
        _merge(seed, [])


@pytest.mark.asyncio
async def test_lifespan_seed_failure_is_fatal():
    """If load_seed() raises, lifespan must propagate — app must not start."""
    from main import lifespan
    from fastapi import FastAPI

    app = FastAPI()
    with patch("chromadb.HttpClient"), \
            patch("main.load_seed", side_effect=RuntimeError("Seed file not found")):
        with pytest.raises(RuntimeError, match="Seed file not found"):
            async with lifespan(app):
                pass


@pytest.mark.asyncio
async def test_lifespan_chroma_failure_is_non_fatal():
    """If _sync_to_chroma raises, lifespan must still yield — app starts in degraded mode."""
    from main import lifespan, qa_cache
    from fastapi import FastAPI

    seed_data = [{"question": "Q1", "answer": "A1", "topic": "c", "tags": ["c"]}]
    app = FastAPI()

    with patch("chromadb.HttpClient"), \
            patch("main.load_seed", return_value=seed_data), \
            patch("main.load_db_pairs", new_callable=AsyncMock, return_value=[]), \
            patch("main._sync_to_chroma", new_callable=AsyncMock,
                  side_effect=RuntimeError("ChromaDB down")), \
            patch("main.get_embeddings", side_effect=RuntimeError("ChromaDB down")):
        async with lifespan(app):
            assert len(qa_cache["qa_pairs"]) == 1


@pytest.mark.asyncio
async def test_lifespan_happy_path():
    """Full successful startup populates qa_cache."""
    from main import lifespan, qa_cache
    from fastapi import FastAPI

    seed_data = [{"question": "Q1", "answer": "A1", "topic": "c", "tags": ["c"]}]
    app = FastAPI()

    with patch("chromadb.HttpClient"), \
            patch("main.load_seed", return_value=seed_data), \
            patch("main.load_db_pairs", new_callable=AsyncMock, return_value=[]), \
            patch("main._sync_to_chroma", new_callable=AsyncMock), \
            patch("main.get_embeddings", side_effect=lambda ids: {id_: [0.1] * 768 for id_ in ids}):
        async with lifespan(app):
            assert len(qa_cache["qa_pairs"]) == 1
        assert qa_cache["qa_pairs"] == []


@pytest.mark.asyncio
async def test_lifespan_sets_app_state():
    """app.state must have bm25, id_to_text, centroids, id_to_topic after startup."""
    from main import lifespan
    from fastapi import FastAPI

    seed_data = [
        {"question": "Q1", "answer": "A1", "topic": "codexion", "tags": ["tag1"]},
        {"question": "Q2", "answer": "A2", "topic": "fly-in", "tags": ["tag2"]},
    ]
    app = FastAPI()
    with patch("chromadb.HttpClient"), \
        patch("main.load_seed", return_value=seed_data), \
        patch("main.load_db_pairs", new_callable=AsyncMock, return_value=[]), \
        patch("main._sync_to_chroma", new_callable=AsyncMock), \
        patch("main.get_embeddings",
              side_effect=lambda ids: {id_: [0.1 * (i + 1)] * 768 for i, id_ in enumerate(ids)}):
        async with lifespan(app):
            assert hasattr(app.state, "bm25")
            assert hasattr(app.state, "id_to_text")
            assert hasattr(app.state, "centroids")
            assert hasattr(app.state, "id_to_topic")
            assert hasattr(app.state, "numpy_index")   # added in Step 2 perf optimisation
            assert "codexion" in app.state.centroids
            assert "fly-in" in app.state.centroids
            assert len(app.state.centroids["codexion"]) == 768
