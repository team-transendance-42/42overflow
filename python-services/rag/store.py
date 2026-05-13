from   urllib.parse import urlparse
import chromadb
from   config import CHROMA_URL

'''
ChromaDB is a special database designed for storing and searching vectors (embeddings), handles high-dimensional data. The functs here are focused on managing a collection of question-answer pairs, where each pair is represented as a document with an associated embedding and metadata.
'''

_DEFAULT_COLLECTION = "qa_pairs"

# create a client connection to ChromaDB using the provided URL. 
"""
Create a client connection to ChromaDB using the provided URL from config.
"""
def _client() -> chromadb.HttpClient:
    parsed = urlparse(CHROMA_URL)
    return chromadb.HttpClient(host=parsed.hostname, port=parsed.port)


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
        _client().get_or_create_collection(name)
    except Exception as exc:
        raise _chroma_error("ensure_collection", exc) from exc


# doc_hash is a unique ID for the content of a document, created using a hash function, and stored as metadata in ChromaDB for quick comparison and version control.
"""
Get the doc_hash metadata for a list of document IDs from ChromaDB.
Used to check if documents are up to date.
"""
def get_existing_hashes(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict[str, str]:
    try:
        col = _client().get_or_create_collection(name)
        result = col.get(ids=ids, include=["metadatas"])
    except Exception as exc:
        raise _chroma_error("get_existing_hashes", exc) from exc

    return {
        doc_id: meta["doc_hash"]
        for doc_id, meta in zip(result["ids"], result["metadatas"])
        if meta and "doc_hash" in meta
    }


# Insert or update documents in the ChromaDB collection. (upsert)
# This func stores the document text, its embedding, and metadata for each document in the specified collection. Useful for keeping the vector database in sync with the latest data.
# wrapper for build in upsert func of chromadb
"""
Insert or update (upsert) documents, embeddings, and metadata in the ChromaDB collection.
Keeps the vector database in sync with the latest data.
"""
def upsert(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
    name: str = _DEFAULT_COLLECTION,
) -> None:
    try:
        col = _client().get_or_create_collection(name)
        col.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    except Exception as exc:
        raise _chroma_error("upsert", exc) from exc


def retrieve(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict:
    """Fetch documents, embeddings, and metadatas for the given IDs from ChromaDB."""
    try:
        col = _client().get_or_create_collection(name)
        return col.get(ids=ids, include=["embeddings", "documents", "metadatas"])
    except Exception as exc:
        raise _chroma_error("retrieve", exc) from exc


# performs a vector similarity search in a ChromaDB collection(table)
# Takes an embedding (a list of floats representing a vector), a number n, and a collection name.
# Connects to ChromaDB and retrieves the specified collection.Uses ChromaDB’s HNSW index to find the n most similar vectors (nearest neighbors) to the given embedding in the collection.
# Returns a list of dictionaries, each containing the id, document, and distance (similarity score) for each neighbor, sorted by similarity (most similar first).
def query_dense(
    embedding: list[float],
    n: int = 20,
    name: str = _DEFAULT_COLLECTION,
) -> list[dict]:
    """
    Find the n nearest neighbours to embedding in the collection.

    Uses ChromaDB's HNSW index under the hood — approximate nearest
    neighbour search (O(log n)) rather than brute-force (O(n)).
    Distance metric is L2 by default for ChromaDB collections; lower
    distance = more similar.

    Returns: [{"id": ..., "document": ..., "distance": ...}, ...]
    sorted by ascending distance (most similar first).
    """
    try:
        col = _client().get_or_create_collection(name)
        result = col.query(
            query_embeddings=[embedding],
            n_results=min(n, col.count()),  # guard: can't request more than collection size
            include=["documents", "distances"],
        )
    except Exception as exc:
        raise _chroma_error("query_dense", exc) from exc

    ids        = result["ids"][0]
    documents  = result["documents"][0]
    distances  = result["distances"][0]
    return [
        {"id": id_, "document": doc, "distance": dist}
        for id_, doc, dist in zip(ids, documents, distances)
    ]
