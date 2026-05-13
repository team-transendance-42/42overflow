import hashlib
import httpx
from config import EMBED_MODEL, OLLAMA_URL


def format_doc(question: str, answer: str) -> str:
    return f"Q: {question}\nA: {answer}"

# encode() changes text into bytes, which is required for hashing functions. The hashlib.sha256() takes bytes as input and produces a hash object. The hexdigest() method converts the hash object into a hexadecimal string representation, which is easier to store and compare.
def make_doc_id(question: str) -> str:
    return hashlib.sha256(question.encode()).hexdigest()


def make_doc_hash(question: str, answer: str) -> str:
    return hashlib.sha256((question + answer).encode()).hexdigest()

# httpx is a Python library for sending HTTP requests.
# AsyncClient is a class that lets you send requests without blocking your program, so you can do other things while waiting for a response.
# When an exception is raised, Python checks the call stack (the list of functions that were called) for any except blocks.
# If none are found, Python prints the error and exits.
# A coroutine is a special type of func that can pause and resume its execution, allowing you to write async code. Coroutines are used for tasks like network requests or file I/O, where you want your program to do other things while waiting.
# When called, it returns a coroutine object (not the result).
# You run (or “await”) it using the await keyword or an event loop.
async def embed_texts(texts: list[str]) -> list[list[float]]:
    ''' Sends a POST req to Ollama API to get embeddings for the given texts. The req includes the model name and the input texts in JSON format. The response is expected to contain a list of embeddings, which are returned as a list of lists of floats.
    '''
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_URL}/api/embed",
                json={"model": EMBED_MODEL, "input": texts},
                timeout=120.0,
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                f"Ollama timed out after 120s (url={OLLAMA_URL}, model={EMBED_MODEL})"
            ) from None
        except httpx.RequestError as exc:
            raise RuntimeError(f"Could not reach Ollama at {OLLAMA_URL}: {exc}") from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Ollama returned HTTP error {exc.response.status_code}: {exc}"
            ) from exc

        data = response.json()
        try:
            return data["embeddings"]
        except KeyError:
            raise RuntimeError(
                f"Ollama response missing 'embeddings' key. Got keys: {list(data.keys())}"
            ) from None
        # example:
        #   { "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        #     "other_info": "something"
        #   }
