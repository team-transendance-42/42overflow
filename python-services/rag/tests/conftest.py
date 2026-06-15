"""
Shared pytest fixtures.

mock_chroma_client: autouse fixture that patches chromadb.HttpClient before
any test that lazily imports store/main. Without this, store._client =
_make_client() at module-import time tries to connect and fails in unit tests
(no docker). Integration tests (test_retriever, test_router) run inside
the container where ChromaDB IS running, so the mock is transparent there
— the real client has already been created before pytest starts.
"""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_chroma_client():
    """Prevent chromadb from connecting in unit tests (no docker needed)."""
    with patch("chromadb.HttpClient", return_value=MagicMock()):
        yield
