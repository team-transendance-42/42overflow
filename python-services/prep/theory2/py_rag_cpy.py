import math  # sqrt, log | math ops
import re  # sub | regex
from collections import Counter  # Counter | counting
from pathlib import Path  # Path | file paths

def load_documents(directory: str) -> dict[str, str]:
    docs = {}  # 1. Empty dictionary(map: key-val) to hold results
    for path in Path(directory).glob("*.md"):  # glob is genexpr
        docs[path.name] = path.read_text(encoding="utf-8")  # 2a-c. Read and store file content
    return docs  # 3. Return the dictionary

# chunk size 150, overlap 30: 1-150, 121-270, 241-390, etc. (overlap 30 means next chunk starts 30 words before previous chunk ends)
# returns a list of strings, each being a chunk of up to 150 words from the text.
# The next chunk starts 120 words after the previous chunk started, so it overlaps the previous chunk by 30 words.
# This way, important information near the boundaries isn’t lost between chunks.
def chunk_text(text: str, chunk_size: int = 150, overlap: int = 30) -> list[str]:
    words = text.split() # split str into arr on whitespace
    chunks: list[str] = [] # []string{} in Go — empty result array
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap
    return chunks

# re.sub(r"..r means a row string: \ no special char") from re(regex) module: replace parts of a str matching a pattern with a replacement
# [ ... ] — List comprehension: creates a new list.
# use on each chunk
def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text) # replace non-alphanumeric chars with space; \s is whitespace
    return [t for t in text.split() if len(t) > 1] # split on whitespace, filter out single-char tokens, return arr(list) of tokens

class TFIDFVectorizer:
    def __init__(self) -> None:
        self.idf: dict[str, float] = {}
        self.corpus_size: int = 0

    # the method name fit(means learn from data: build a frequency table) is used to indicate that the function is training or building a model based on input data
    # populate class fields, idf: frequency of words(tokens) used in all docs in corpus
    def fit(self, corpus: list[str]) -> None:
        self.corpus_size = len(corpus)
        df: Counter = Counter()
        for doc in corpus:
            for token in set(tokenize(doc)):
                df[token] += 1
        self.idf = { # dictionary comprehension: create a new dict by looping over items etc
            key: math.log(self.corpus_size / (1 + val)) + 1
            for key, val in df.items()
        }

    # theory: Dense vector (array):   [0.0,  0.42, 0.0,  0.0,  0.61]
    #                                  bites  dog   fast   man   runs

    # Sparse vector (dict, aka map(key, val)):   {"dog": 0.42, "runs": 0.61}
    #                          ← only non-zero terms stored
    # The func is called transform: follows naming convention in machine learning libraries like scikit-learn. there transform means "convert input data into a new representation" using what was learned during fit
    def transform(self, text: str) -> dict[str, float]:
        tokens = tokenize(text)
        if not tokens:
            return {}
        tf = Counter(tokens)  # term frequency in the text
        total = len(tokens)
        return {
            key: (val / total) * self.idf[key]
            for key, val in tf.items() if key in self.idf
        }

    def fit_transform(self, corpus: list[str]) -> list[dict[str, float]]:
        self.fit(corpus) # populate class fields
        return [self.transform(doc) for doc in corpus]

# ======== cosine similarity: measure of similarity between two vectors, ranges from -1 to 1. 1 means identical, 0 means orthogonal (no similarity), -1 means opposite.
# explained in cosine_similarity.txt
# cos(θ) = (A · B) / (|A| × |B|) dot product of v1 and v2 / magntitude(lenght) of v1 * magnitude of v2
def cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    if not vec1 or not vec2:
        return 0.0
    dot = sum(vec1[key] * vec2[key] for key in vec1 if key in vec2)
    mag1 = math.sqrt(sum(val * val for val in vec1.values()))
    mag2 = math.sqrt(sum(val * val for val in vec2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

# ============== A vector store holds two parallel arrays per chunk:
#   • texts    → original strings returned as context to the LLM
#   • vectors  → embeddings used for similarity scoring
#   • metadata → provenance (source file, chunk index) for citation / debugging

class VectorStore:
    def __init__(self) -> None:
        self.texts: list[str] = []
        self.vectors: list[dict[str, float]] = []
        self.metadata: list[dict] = []
    
    def add(self, text: str, vector: dict[str, float], meta: dict | None = None) -> None:
        self.texts.append(text)
        self.vectors.append(vector)
        self.metadata.append(meta or {})

    def __len__(self) -> int:
        return len(self.texts)

#  retrieve
def retrieve(query: str, store: VectorStore,
    vectorizer: TFIDFVectorizer, n: int = 3,) -> list[tuple[float, str, dict]]:
    query_vec = vectorizer.transform(query)
    scored = [(cosine_similarity(query_vec, vec), text, meta)
        for vec, text, meta in zip(store.vectors, store.texts, store.metadata)]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:n]

# prompt construction
#  Retrieved chunks become the *context window* injected into the LLM prompt.
# This is the "Augmented" part of Retrieval-Augmented Generation.
#
# Standard RAG prompt structure:
#   [System]    You are a helpful assistant. Answer ONLY from the context below.
#   [Context]   <chunk 1>  ---  <chunk 2>  ---  ...
#   [Question]  <user question>
#
# Why "answer ONLY from context"?
#   Forces the model to ground its answer in retrieved facts instead of
#   hallucinating from pre-training weights. The model may still reason and
#   rephrase, but should not invent facts absent from the context.
#
# Including the score and source in each chunk block helps the LLM (and the
# developer) understand which sources were used — useful for citation generation.
def build_prompt(question: str, results: list[tuple[float, str, dict]]) -> str:
    context_parts = []
    for i, (score, text, meta) in enumerate(results, 1):
        source = meta.get("source", "?")
        context_parts.append(
            f"[Context {i}] source={source} relevance={score:.3f}\n{text}"
        )
    context = "\n\n---\n\n".join(context_parts)
    return (
        "You are a knowledgeable assistant.\n"
        "Answer using ONLY the context provided. "
        "If the context is insufficient, say so.\n\n"
        f"=== CONTEXT ===\n{context}\n\n"
        f"=== QUESTION ===\n{question}\n\n"
        f"=== ANSWER ==="
    )

# generate
def generate(prompt: str) -> str:
    # In a real implementation, this would call an LLM API (e.g., OpenAI, Hugging Face).
    # For this theory example, we’ll just return a placeholder string.
    border = "-" * 72
    lines = [
        f"\n{border}",
        border,
        prompt,
        border,
        "connect to ollama here to ger e real answer",
        border,
    ]
    return "\n".join(lines)

#  Indexing (Load → Chunk → Embed → Store) happens ONCE (or on document update).
# It is expensive: embedding N chunks takes O(N × chunk_size) time.
# In production the index is persisted to disk / a vector DB so it survives restarts.
# Query time (Embed query → Retrieve → Generate) is cheap: one embedding + k dot products.
def build_index(docs_dir: str) -> tuple[VectorStore, TFIDFVectorizer, list[str]]:
    docs = load_documents(docs_dir)
    if not docs:
        raise FileNotFoundError(f"No .md files found in the {docs_dir} dir.")

    all_chunks: list[str] = []
    all_metas: list[dict] = []

    for key, val in docs.items():
        for i, chunk in enumerate(chunk_text(val)):
            all_chunks.append(chunk)
            all_metas.append({"source": key, "chunk_idx": i})

    print(f"[INDEX] {len(docs)} docs -> {len(all_chunks)} chunks")

    vectorizer = TFIDFVectorizer()
    vectors = vectorizer.fit_transform(all_chunks)

    store = VectorStore()
    for chunk, vector, meta in zip(all_chunks, vectors, all_metas):
        store.add(chunk, vector, meta)

    print(f"[index] vocabulary: {len(vectorizer.idf)} unique terms")
    return store, vectorizer, list(docs.keys())

# # ── 11. Query Interface ───────────────────────────────────────────────────────
# THEORY: At query time the steps are:
#   1. Embed the question (same vectorizer, same IDF weights — same vector space).
#   2. Retrieve top-k most similar chunks (nearest neighbours).
#   3. Assemble context → build prompt.
#   4. Send prompt to LLM → return answer.
# Latency budget in production: embedding ~5 ms, retrieval ~2 ms, LLM ~500-2000 ms.

def ask(q: str, store: VectorStore, vectorizer: TFIDFVectorizer, n: int = 3) -> str:
    print(f"\n[query] {q!r} (top-{n} chunks)")
    retrieved = retrieve(q, store, vectorizer, n)

    for score, text, meta in retrieved:
        preview = text[:90].replace("\n", " ")
        print(f" {score:.3f} {meta['source']} \"{preview}...\"")

    prompt = build_prompt(q, retrieved)
    return generate(prompt)



# python3 python-services/rag/theory/rag_cpy.py
def main():
    docs_dir = str(Path(__file__).parent)
    docs = load_documents(docs_dir)
    if not docs:
        print("No .md files found in the dir.md")
        return
    print(f"Found {len(docs)} files")
    filename, content = list(docs.items())[0]
    chunks = chunk_text(content, 15, 3) # chunk is long 15 words
    print(f"{filename}: {len(content)} chars, {len(chunks)} chunks of 150 words with 30 word overlap")
    vectorizer = TFIDFVectorizer()
    vectorizer.fit(chunks)
    print(f"IDF values for {filename}")
    count = 0
    for term, idf in vectorizer.idf.items():
        print(f"  {term}: {idf:.2f}")
        count += 1
        if count >= 5: break

    print(f"Sparse vector values for corresponding terms:")
    vectorized_chunks = vectorizer.fit_transform(chunks)
    for key, val in enumerate(vectorized_chunks[:5]):
        print(f"  Chunk {key+1}: {val}")


def test_untested_funcs():
    docs_dir = str(Path(__file__).parent)

    # cosine_similarity
    print("\n=== cosine_similarity ===")
    va = {"python": 0.5, "vector": 0.4, "search": 0.3}
    vb = {"python": 0.6, "vector": 0.2, "database": 0.1}
    vc = {"banana": 0.9, "fruit": 0.7}
    print(f"  similar:   {cosine_similarity(va, vb):.4f}  (expect high, shared keys)")
    print(f"  unrelated: {cosine_similarity(va, vc):.4f}  (expect 0.0, no shared keys)")

    # VectorStore
    print("\n=== VectorStore ===")
    store = VectorStore()
    store.add("Paris is the capital of France", {"paris": 0.6, "capital": 0.5}, {"source": "geo.md"})
    store.add("Python is a programming language", {"python": 0.7, "programming": 0.4}, {"source": "cs.md"})
    print(f"  added 2 items, len={len(store)}  (expect 2)")

    # build_index
    print("\n=== build_index ===")
    store, vectorizer, filenames = build_index(docs_dir)
    print(f"  files: {filenames}")

    # retrieve
    print("\n=== retrieve ===")
    results = retrieve("what is TF-IDF", store, vectorizer, n=3)
    for score, text, meta in results:
        print(f"  {score:.4f} | {meta['source']} | {text[:60]}...")

    # build_prompt
    print("\n=== build_prompt ===")
    prompt = build_prompt("what is TF-IDF", results)
    print(prompt[:400])
    print("...[truncated]")

    # generate (hardcoded LLM reply instead of real API call)
    print("\n=== generate (hardcoded LLM reply) ===")
    FAKE_LLM_REPLY = "TF-IDF stands for Term Frequency-Inverse Document Frequency. It weights words by how often they appear in a chunk vs how rare they are across all chunks."
    print(f"  hardcoded reply: {FAKE_LLM_REPLY}")

    # ask (full pipeline, swap generate for hardcoded reply)
    print("\n=== ask (full pipeline) ===")
    results = retrieve("what is cosine similarity", store, vectorizer, n=2)
    prompt = build_prompt("what is cosine similarity", results)
    answer = FAKE_LLM_REPLY  # in production: send prompt to Ollama/OpenAI and get real answer
    print(f"  prompt built: {len(prompt)} chars")
    print(f"  answer: {answer}")


if __name__ == "__main__":
    main()
    test_untested_funcs()
    