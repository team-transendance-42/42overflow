from urllib.parse import urlparse # for breaking apart URLs (like “http://localhost:8000”) into pieces (host, port, etc.).

import chromadb
from config import CHROMA_URL

'''
ChromaDB is a special database designed for storing and searching vectors (embeddings). It's built to handle high-dimensional data, which is perfect for AI tasks like similarity search in RAG. The functions here are focused on managing a collection of question-answer pairs, where each pair is represented as a document with an associated embedding and metadata.
'''

_DEFAULT_COLLECTION = "qa_pairs"


def _client() -> chromadb.HttpClient:
    parsed = urlparse(CHROMA_URL)
    return chromadb.HttpClient(host=parsed.hostname, port=parsed.port)


def ensure_collection(name: str = _DEFAULT_COLLECTION) -> None:
    _client().get_or_create_collection(name)


# doc_hash is a unique ID for the content of a document, created using a hash function, and stored as metadata in ChromaDB for quick comparison and version control.
def get_existing_hashes(ids: list[str], name: str = _DEFAULT_COLLECTION) -> dict[str, str]:
    col = _client().get_or_create_collection(name)
    result = col.get(ids=ids, include=["metadatas"])
    return {
        doc_id: meta["doc_hash"]
        for doc_id, meta in zip(result["ids"], result["metadatas"])
        if meta and "doc_hash" in meta
    }


# Insert or update documents in the ChromaDB collection. (upsert)
# This func stores the document text, its embedding, and metadata for each document in the specified collection. Useful for keeping the vector database in sync with the latest data.
# wrapper for build in upsert func of chromadb
def upsert(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
    name: str = _DEFAULT_COLLECTION,
) -> None:
    col = _client().get_or_create_collection(name)
    col.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
