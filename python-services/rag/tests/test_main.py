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


# ── _load_pairs ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_load_pairs_rejects_missing_question_key():
    """_load_pairs must raise ValueError if any pair lacks 'question'."""
    from main import _load_pairs
    with patch("main.load_seed", return_value=[{"answer": "A1", "topic": "c", "tags": []}]):
        with pytest.raises(ValueError, match="missing required"):
            await _load_pairs(include_db=False, label="test")


@pytest.mark.asyncio
async def test_load_pairs_rejects_missing_answer_key():
    """_load_pairs must raise ValueError if any pair lacks 'answer'."""
    from main import _load_pairs
    with patch("main.load_seed", return_value=[{"question": "Q1", "topic": "c", "tags": []}]):
        with pytest.raises(ValueError, match="missing required"):
            await _load_pairs(include_db=False, label="test")


@pytest.mark.asyncio
async def test_load_pairs_skips_db_when_include_db_false():
    """_load_pairs with include_db=False must not call load_db_pairs."""
    from main import _load_pairs
    seed = [{"question": "Q1", "answer": "A1", "topic": "c", "tags": []}]
    mock_db = AsyncMock(return_value=[])
    with patch("main.load_seed", return_value=seed), \
         patch("main.load_db_pairs", mock_db):
        pairs = await _load_pairs(include_db=False, label="test")
    assert len(pairs) == 1
    mock_db.assert_not_called()


# ── _prepare_corpus ───────────────────────────────────────────────────────────

def test_prepare_corpus_builds_all_fields():
    """_prepare_corpus must populate all six keys from a pair list."""
    from main import _prepare_corpus
    pairs = [
        {"question": "Q1", "answer": "A1", "topic": "c",  "tags": ["intro"]},
        {"question": "Q2", "answer": "A2", "topic": "go", "tags": []},
    ]
    corpus = _prepare_corpus(pairs, label="test")
    assert len(corpus["all_texts"]) == 2
    assert len(corpus["all_ids"]) == 2
    assert corpus["all_topics"] == ["c", "go"]
    assert "c" in corpus["topic_intro_ids"]
    assert "go" not in corpus["topic_intro_ids"]
    assert len(corpus["id_to_text"]) == 2
    assert len(corpus["id_to_topic"]) == 2


def test_prepare_corpus_duplicate_intro_keeps_first():
    """Duplicate intro tags for the same topic must keep the first, ignore the second."""
    from main import _prepare_corpus
    from embedder import make_doc_id
    pairs = [
        {"question": "Q1", "answer": "A1", "topic": "c", "tags": ["intro"]},
        {"question": "Q2", "answer": "A2", "topic": "c", "tags": ["intro"]},
    ]
    corpus = _prepare_corpus(pairs, label="test")
    assert corpus["topic_intro_ids"]["c"] == make_doc_id("Q1")


# ── _fetch_embeddings ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_embeddings_returns_empty_on_sync_failure():
    """_fetch_embeddings must return ([], {}) if ChromaDB sync raises."""
    from main import _fetch_embeddings
    pairs = [{"question": "Q1", "answer": "A1", "topic": "c", "tags": []}]
    with patch("main._sync_to_chroma", new_callable=AsyncMock,
               side_effect=RuntimeError("ChromaDB down")):
        emb, centroids = await _fetch_embeddings(pairs, ["id-1"], label="test")
    assert emb == [] and centroids == {}


@pytest.mark.asyncio
async def test_fetch_embeddings_returns_empty_on_get_embeddings_failure():
    """_fetch_embeddings must return ([], {}) if fetching stored embeddings raises."""
    from main import _fetch_embeddings
    pairs = [{"question": "Q1", "answer": "A1", "topic": "c", "tags": []}]
    with patch("main._sync_to_chroma", new_callable=AsyncMock), \
         patch("main.get_embeddings", side_effect=RuntimeError("Chroma timeout")):
        emb, centroids = await _fetch_embeddings(pairs, ["id-1"], label="test")
    assert emb == [] and centroids == {}


# ── admin_seed_postgres error paths ──────────────────────────────────────────

def test_seed_postgres_connect_failure_returns_503():
    """Postgres connection failure must return 503 with a diagnostic message."""
    from main import app
    import main as m
    original_token = m.ADMIN_TOKEN
    m.ADMIN_TOKEN = "test-token"
    try:
        with patch("main.asyncpg.connect", new_callable=AsyncMock,
                   side_effect=OSError("Connection refused")), \
             patch("main.DB_URL", "postgresql://fake/testdb"):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/admin/seed-postgres", json={},
                               headers={"X-Admin-Token": "test-token"})
        assert resp.status_code == 503
        assert "Postgres" in resp.json()["detail"]
    finally:
        m.ADMIN_TOKEN = original_token


def test_seed_postgres_operation_failure_returns_500():
    """DB operation failure must return 500 with the exception text as detail."""
    from main import app
    import main as m
    original_token = m.ADMIN_TOKEN
    m.ADMIN_TOKEN = "test-token"
    try:
        with patch("main.asyncpg.connect", new_callable=AsyncMock) as mock_connect, \
             patch("main.DB_URL", "postgresql://fake/testdb"), \
             patch("main.ensure_users", new_callable=AsyncMock,
                   side_effect=RuntimeError("relation \"User\" does not exist")):
            mock_connect.return_value = AsyncMock()
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/admin/seed-postgres", json={},
                               headers={"X-Admin-Token": "test-token"})
        assert resp.status_code == 500
        assert "User" in resp.json()["detail"]
    finally:
        m.ADMIN_TOKEN = original_token


# ── existing endpoint tests ───────────────────────────────────────────────────

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
