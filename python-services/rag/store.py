from urllib.parse import urlparse
import chromadb
from chromadb.config import Settings
from config import CHROMA_URL

'''
ChromaDB is a special database designed for storing and searching vectors
(embeddings), handles high-dimensional data. The functs here are focused on
managing a collection of question-answer pairs, where each pair is represented
as a document with an associated embedding and metadata.
each collection(table) stores fields:
id: str — unique identifier for the document
document: str — the main text/content
embedding: list[float] — the vector representation of the document
metadatas: dict — extra info (e.g., doc_hash, tags, etc.)
'''

_DEFAULT_COLLECTION = "qa_pairs"


def _make_client() -> chromadb.HttpClient:
    parsed = urlparse(CHROMA_URL)
    return chromadb.HttpClient(
        host=parsed.hostname,
        port=parsed.port,
        settings=Settings(anonymized_telemetry=False),
    )


# Both client and collection are lazily initialised so that a ChromaDB container
# that is slow to start (or temporarily down) does not crash the import and does
# not prevent FastAPI from starting in degraded/seed-only mode.
# chromadb.HttpClient() performs a heartbeat HTTP request in its constructor, so
# calling _make_client() at module level would fail if ChromaDB is unreachable.
_client = None
_collection = None


def _get_client() -> chromadb.HttpClient:
    global _client
    if _client is None:
        _client = _make_client()
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(_DEFAULT_COLLECTION)
    return _collection


def _invalidate_collection() -> None:
    """Reset cached collection after a ChromaDB error so the next call re-connects."""
    global _collection
    _collection = None


def clear_collection(name: str = _DEFAULT_COLLECTION) -> int:
    """Delete all documents from the ChromaDB collection. Returns count deleted."""
    try:
        col = _get_collection()
        count = col.count()
        if count > 0:
            all_ids = col.get(include=[])["ids"]
            col.delete(ids=all_ids)
        return count
    except Exception as exc:
        _invalidate_collection()
        raise _chroma_error("clear_collection", exc) from exc


def _chroma_error(operation: str, exc: Exception) -> RuntimeError:
    return RuntimeError(
        f"Could not connect to ChromaDB during '{operation}' (url={CHROMA_URL}): {exc}"
    )


def get_embeddings(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict[str, list[float]]:
    """Fetch stored embeddings from ChromaDB for the given IDs. Returns id → embedding."""
    try:
        result = _get_collection().get(ids=ids, include=["embeddings"])
    except Exception as exc:
        _invalidate_collection()
        raise _chroma_error("get_embeddings", exc) from exc
    return {
        doc_id: emb
        for doc_id, emb in zip(result["ids"], result["embeddings"])
    }


def get_existing_hashes(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict[str, str]:
    try:
        result = _get_collection().get(ids=ids, include=["metadatas"])
    except Exception as exc:
        _invalidate_collection()
        raise _chroma_error("get_existing_hashes", exc) from exc
    return {
        doc_id: meta["doc_hash"]
        for doc_id, meta in zip(result["ids"], result["metadatas"])
        if meta and "doc_hash" in meta
    }


def upsert(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
    name: str = _DEFAULT_COLLECTION,
) -> None:
    try:
        _get_collection().upsert(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )
    except Exception as exc:
        _invalidate_collection()
        raise _chroma_error("upsert", exc) from exc


# NOT USED in production — only called from tests/flow_seed_embed_store.py.
# NumpyIndex replaced both functions below for all query-time retrieval.
# Kept commented so tests still document what ChromaDB used to provide.

# def retrieve(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict:
#     """Fetch documents, embeddings, and metadatas for the given IDs from ChromaDB."""
#     try:
#         col = _get_collection()
#         return col.get(ids=ids, include=["embeddings", "documents", "metadatas"])
#     except Exception as exc:
#         _invalidate_collection()
#         raise _chroma_error("retrieve", exc) from exc


# NOT USED in production — replaced by NumpyIndex.search().
# ChromaDB HNSW search cost: ~50-150ms network roundtrip per call.
# NumpyIndex cosine similarity cost: ~0.05ms in-process matrix multiply.
# Kept commented to document the ChromaDB-based approach for reference.

# def query_dense(
#     embedding:    list[float],
#     n:            int = 20,
#     topic_filter: str | None = None,
#     name:         str = _DEFAULT_COLLECTION,
# ) -> list[dict]:
#     try:
#         col   = _get_collection()
#         where = {"topic": topic_filter} if topic_filter else None
#         safe_n = min(n, col.count())
#         if safe_n == 0:
#             return []
#         result = col.query(
#             query_embeddings=[embedding],
#             n_results=safe_n,
#             where=where,
#             include=["documents", "distances"],
#         )
#     except Exception as exc:
#         _invalidate_collection()
#         raise _chroma_error("query_dense", exc) from exc
#     ids       = result["ids"][0]
#     documents = result["documents"][0]
#     distances = result["distances"][0]
#     return [
#         {"id": id_, "document": doc, "distance": dist}
#         for id_, doc, dist in zip(ids, documents, distances)
#     ]
