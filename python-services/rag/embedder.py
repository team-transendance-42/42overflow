import asyncio
import hashlib

from fastembed import TextEmbedding

# Loaded once at module import — stays in RAM, reused on every request.
# fastembed downloads the model to ~/.cache/fastembed/ on first use;
# the Dockerfile pre-downloads it at build time so container startup is instant.
_model = TextEmbedding("nomic-ai/nomic-embed-text-v1.5")


def format_doc(question: str, answer: str) -> str:
    """Format a QA pair for storage in ChromaDB and BM25 indexing."""
    return f"Q: {question}\nA: {answer}"


def make_doc_id(question: str) -> str:
    """Stable unique ID for a document, derived from the question text."""
    return hashlib.sha256(question.encode()).hexdigest()


def make_doc_hash(question: str, answer: str) -> str:
    return hashlib.sha256((question + answer).encode()).hexdigest()


def _embed_sync(texts: list[str]) -> list[list[float]]:
    return [vec.tolist() for vec in _model.embed(texts)]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts using the local nomic-embed-text-v1.5 model.

    Runs in a thread pool — fastembed is CPU-bound and must not block
    the async event loop. Returns one 768-dim vector per input text.
    """
    if not texts:
        raise RuntimeError("embed_texts called with empty list")
    return await asyncio.to_thread(_embed_sync, texts)
