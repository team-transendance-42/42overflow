"""
Tests for main.py startup logic.
Run: uv run python -m pytest tests/test_main.py -v
No live services needed — all external calls are mocked.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient



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


@pytest.mark.asyncio
async def test_lifespan_does_not_call_load_db_pairs():
    """Startup must be seed-only — load_db_pairs must not be called at boot."""
    from main import lifespan
    from fastapi import FastAPI
    from unittest.mock import AsyncMock, patch

    seed_data = [{"question": "Q1", "answer": "A1", "topic": "c", "tags": ["c"]}]
    mock_db = AsyncMock(return_value=[{"question": "DB-Q", "answer": "DB-A", "topic": "c", "tags": []}])
    app = FastAPI()

    with patch("chromadb.HttpClient"), \
            patch("main.load_seed", return_value=seed_data), \
            patch("main.load_db_pairs", mock_db), \
            patch("main._sync_to_chroma", new_callable=AsyncMock), \
            patch("main.get_embeddings", side_effect=lambda ids: {id_: [0.1] * 768 for id_ in ids}):
        async with lifespan(app):
            pass

    mock_db.assert_not_called()


def test_seed_postgres_missing_token_returns_403():
    from main import app
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/admin/seed-postgres")
    assert resp.status_code == 403


def test_seed_postgres_wrong_token_returns_403():
    from main import app
    import main as m
    original = m.ADMIN_TOKEN
    m.ADMIN_TOKEN = "correct-token"
    try:
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/admin/seed-postgres", headers={"X-Admin-Token": "wrong"})
        assert resp.status_code == 403
    finally:
        m.ADMIN_TOKEN = original


def test_seed_postgres_happy_path():
    from main import app
    import main as m

    original_token = m.ADMIN_TOKEN
    m.ADMIN_TOKEN = "test-token"

    try:
        with patch("main.asyncpg.connect", new_callable=AsyncMock) as mock_connect, \
             patch("main.DB_URL", "postgresql://fake/testdb"), \
             patch("main.ensure_users", new_callable=AsyncMock), \
             patch("main.ensure_subjects", new_callable=AsyncMock, return_value={"push_swap": 1}), \
             patch("main.clean_posts", new_callable=AsyncMock), \
             patch("main.insert_posts", new_callable=AsyncMock, return_value=(3, 0)):
            mock_conn = AsyncMock()
            mock_connect.return_value = mock_conn
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/admin/seed-postgres",
                json={},
                headers={"X-Admin-Token": "test-token"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["status"] == "ok"
            assert body["inserted"] == 3
            assert body["skipped"] == 0
    finally:
        m.ADMIN_TOKEN = original_token


def test_seed_postgres_clean_param_calls_clean_posts():
    from main import app
    import main as m

    original_token = m.ADMIN_TOKEN
    m.ADMIN_TOKEN = "test-token"

    try:
        with patch("main.asyncpg.connect", new_callable=AsyncMock) as mock_connect, \
             patch("main.DB_URL", "postgresql://fake/testdb"), \
             patch("main.ensure_users", new_callable=AsyncMock), \
             patch("main.ensure_subjects", new_callable=AsyncMock, return_value={}), \
             patch("main.clean_posts", new_callable=AsyncMock) as mock_clean, \
             patch("main.insert_posts", new_callable=AsyncMock, return_value=(0, 0)):
            mock_connect.return_value = AsyncMock()
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/admin/seed-postgres",
                json={"clean": True},
                headers={"X-Admin-Token": "test-token"},
            )
            assert resp.status_code == 200
            mock_clean.assert_called_once()
    finally:
        m.ADMIN_TOKEN = original_token


def test_sync_chroma_missing_token_returns_403():
    from main import app
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/admin/sync-chroma")
    assert resp.status_code == 403


def test_sync_chroma_wrong_token_returns_403():
    from main import app
    import main as m
    original = m.ADMIN_TOKEN
    m.ADMIN_TOKEN = "correct-token"
    try:
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/admin/sync-chroma", headers={"X-Admin-Token": "wrong"})
        assert resp.status_code == 403
    finally:
        m.ADMIN_TOKEN = original


def test_sync_chroma_happy_path():
    from main import app
    import main as m

    original_token = m.ADMIN_TOKEN
    m.ADMIN_TOKEN = "test-token"

    seed_data = [{"question": "Q1", "answer": "A1", "topic": "c", "tags": ["c"]}]

    try:
        with patch("chromadb.HttpClient"), \
             patch("main.load_seed", return_value=seed_data), \
             patch("main.load_db_pairs", new_callable=AsyncMock, return_value=[]), \
             patch("main._sync_to_chroma", new_callable=AsyncMock), \
             patch("main.get_embeddings", side_effect=lambda ids: {i: [0.1] * 768 for i in ids}):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/admin/sync-chroma",
                headers={"X-Admin-Token": "test-token"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["status"] == "ok"
            assert "total_docs" in body
            assert "embeddings_ready" in body
    finally:
        m.ADMIN_TOKEN = original_token
