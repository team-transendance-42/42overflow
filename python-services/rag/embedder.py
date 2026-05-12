import hashlib
import httpx
from config import EMBED_MODEL, OLLAMA_URL


def format_doc(question: str, answer: str) -> str:
    return f"Q: {question}\nA: {answer}"


def make_doc_id(question: str) -> str:
    return hashlib.sha256(question.encode()).hexdigest()


def make_doc_hash(question: str, answer: str) -> str:
    return hashlib.sha256((question + answer).encode()).hexdigest()


async def embed_texts(texts: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": texts},
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["embeddings"]
