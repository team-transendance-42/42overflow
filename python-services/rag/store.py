from   urllib.parse import urlparse
import chromadb
from chromadb.config import Settings
from   config import CHROMA_URL

'''
ChromaDB is a special database designed for storing and searching vectors (embeddings), handles high-dimensional data. The functs here are focused on managing a collection of question-answer pairs, where each pair is represented as a document with an associated embedding and metadata.
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

# Single persistent client — reuses the TCP connection across all calls.
# Previously _client() was called inside every function, opening a new
# connection on every ChromaDB operation (~50-100ms overhead each time).
_client = _make_client()


def _chroma_error(operation: str, exc: Exception) -> RuntimeError:
    """
    Format a RuntimeError for ChromaDB connection issues, including operation and URL.
    """
    return RuntimeError(
        f"Could not connect to ChromaDB during '{operation}' (url={CHROMA_URL}): {exc}"
    )


def ensure_collection(name: str = _DEFAULT_COLLECTION) -> None:
    """
    Ensure the specified ChromaDB collection exists; create it if missing.
    """
    try:
        _client.get_or_create_collection(name)
    except Exception as exc:
        raise _chroma_error("ensure_collection", exc) from exc


# doc_hash is a unique ID for the content of a document, created using a hash function, and stored as metadata in ChromaDB for quick comparison and version control.
"""
Get the doc_hash metadata for a list of document IDs from ChromaDB.
Used to check if documents are up to date.
"""
def get_existing_hashes(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict[str, str]:
    try:
        col = _client.get_or_create_collection(name)
        result = col.get(ids=ids, include=["metadatas"])
    except Exception as exc:
        raise _chroma_error("get_existing_hashes", exc) from exc

    return {
        doc_id: meta["doc_hash"]
        for doc_id, meta in zip(result["ids"], result["metadatas"])
        if meta and "doc_hash" in meta
    }


"""
Insert or update (upsert) documents, embeddings, and metadata in the ChromaDB collection.
Keeps the vector database in sync with the latest data. Wrapper of ChromaDB's upsert method with error handling.
"""
def upsert(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
    name: str = _DEFAULT_COLLECTION,
) -> None:
    try:
        col = _client.get_or_create_collection(name)
        col.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    except Exception as exc:
        raise _chroma_error("upsert", exc) from exc


def retrieve(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict:
    """Fetch documents, embeddings, and metadatas for the given IDs from ChromaDB."""
    try:
        col = _client.get_or_create_collection(name)
        return col.get(ids=ids, include=["embeddings", "documents", "metadatas"])
    except Exception as exc:
        raise _chroma_error("retrieve", exc) from exc


# performs a vector similarity search in a ChromaDB collection(table)
# Takes an embedding (a list of floats representing a vector), a number n, and a collection name.
# Connects to ChromaDB and retrieves the specified collection. Uses ChromaDB’s HNSW index to find the n most similar vectors (nearest neighbors) to the given embedding in the collection.
# Returns a list of dictionaries, each containing the id, document, and distance (similarity score) for each neighbor, sorted by similarity (most similar first).
def query_dense(
    embedding:    list[float],
    n:            int = 20,
    topic_filter: str | None = None,
    name:         str = _DEFAULT_COLLECTION,
) -> list[dict]:
    """
    Find the n nearest neighbours to embedding in the collection.

    Uses ChromaDB's HNSW index — approximate nearest neighbour search
    (O(log n)) rather than brute-force (O(n)).

    Args:
        embedding:    query vector (768-dim for nomic-embed-text-v1.5).
        n:            max results to return.
        topic_filter: if given, restrict search to docs where metadata
                      topic == topic_filter. None = search full collection.
        name:         ChromaDB collection name.

    Returns: [{"id": ..., "document": ..., "distance": ...}]
    sorted by ascending distance (most similar first).
    """
    try:
        col   = _client.get_or_create_collection(name)
        where = {"topic": topic_filter} if topic_filter else None

        safe_n = min(n, col.count())
        if safe_n == 0:
            return []

        result = col.query(
            query_embeddings=[embedding],
            n_results=safe_n,
            where=where,
            include=["documents", "distances"],
        )
    except Exception as exc:
        raise _chroma_error("query_dense", exc) from exc

    ids       = result["ids"][0]
    documents = result["documents"][0]
    distances = result["distances"][0]
    return [
        {"id": id_, "document": doc, "distance": dist}
        for id_, doc, dist in zip(ids, documents, distances)
    ]
