"""
Simplified RAG (Retrieval-Augmented Generation) — pure Python, zero external deps.
Run: python3 python-services/rag/theory/rag.py

Production RAG lives in: python-services/rag/main.py  (ChromaDB + Ollama + FastAPI)
This file teaches HOW each step works under the hood, bottom-up.
"""

import math  # sqrt, log | math ops
import re  # sub | regex
from collections import Counter  # Counter | counting
from pathlib import Path  # Path | file paths


# ── 1. Document Loading ───────────────────────────────────────────────────────
# THEORY: RAG needs a *knowledge base* — text the LLM doesn't know from training
# (private data, recent events, domain docs). We read raw files here.
# Under the hood: production loaders handle PDFs (PyMuPDF), web pages (BeautifulSoup),
# databases (SQL), APIs, etc. The goal is the same: plain text strings.

def load_documents(directory: str) -> dict[str, str]:
    docs = {}  # 1. Empty dictionary to hold results
    for path in Path(directory).glob("*.md"):  # 2. Loop over all .md files in directory
        docs[path.name] = path.read_text(encoding="utf-8")  # 2a-c. Read and store file content
    return docs  # 3. Return the dictionary


# ── 2. Text Chunking ─────────────────────────────────────────────────────────
# THEORY: We cannot embed (and meaningfully retrieve) a 5 000-word document as
# a single vector — the signal is too diluted. Chunking solves this:
#
#   • Smaller chunks → each vector represents a tighter idea → more precise retrieval.
#   • Overlap (stride < chunk_size) → a key idea split across a boundary still
#     survives whole in the overlapping region of one of the two chunks.
#
# Chunk size trade-off:
#   Too small (< 50 words)  → chunk loses surrounding context; confusing on its own.
#   Too large (> 500 words) → retrieval becomes coarse; LLM gets lots of irrelevant text.
#   Sweet spot: 100-300 words, overlap 10-20 % of chunk size.
#
# In production, chunk on tokens (not words) via tiktoken or HuggingFace tokenizers,
# because LLM context limits are measured in tokens, not words.

# go:  strings.Join([]string{"hello", "world", "foo"}, " ") = " ".join(["hello", "world", "foo"])
#  chunk := strings.TrimSpace(strings.Join(words[start:end], " "))

def chunk_text(text: str, chunk_size: int = 150, overlap: int = 30) -> list[str]:
    """Split text into overlapping word-windows of ~chunk_size words."""
    words = text.split() # on whitespace, get list of words: arr of str
    chunks: list[str] = [] # empty list of type str
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end]).strip() # single str, words separated by " " 
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap  # slide forward, keep overlap words
    return chunks


# ── 3. Tokenization (text preprocessing) ─────────────────────────────────────
# THEORY: Before computing any numerical representation we normalize text so that
# "Python", "python", and "Python," are treated as the same token. Steps:
#   1. Lowercase  → case-insensitivity
#   2. Strip punctuation → "end." == "end"
#   3. Remove very short tokens → single chars add noise, not meaning
# In production: use subword tokenizers (BPE, WordPiece) that handle morphology
# and rare words by breaking them into known sub-units ("un" + "known").

def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, return tokens of length > 1."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 1]


# ── 4. TF-IDF Vectorizer (term frequency - inverse document frequency) ─────────────────────────────────────────────────────
# THEORY: To compare text by *meaning*, turn words into numbers (vectors).
# TF-IDF(term frequency - inverse document frequency) is a classic sparse approach:
#
#   TF(t(term), d(doc))  = count(t in chunk d) / total_tokens(d)
#               ↳ how often does this word appear IN THIS chunk?
#
# IDF measures how rare or unique a term is across all documents (or chunks). The more documents contain t, the lower its IDF
#   IDF(t)    = log( N / (1 + df(t)) ) + 1   ← smoothed variant
#               where N = number of total chunks, df(t) = chunks containing term t
#               ↳ how RARE is this word across ALL chunks?;
#               Common words ("the", "a", "is") → df ≈ N → IDF ≈ 1 → low weight. (N is number of chunks, df is number of chunks containing the term in the document)
#               Rare domain words ("eigenvalue") → df ≈ 1 → IDF ≈ log(N) → high weight.

#               log(logarithm function). For our purposes, it’s just a way to “squash” big numbers into smaller ones, so rare words get higher scores, but not too high.
#             1 + df(t): We add 1 to avoid dividing by zero if a word is super rare.
#             So, IDF(t) = log(N / (1 + df(t))) + 1 means:
#             If a word appears in almost every document, its IDF is low (not special).
#             If a word appears in only a few documents, its IDF is high (it’s rare and important).
#
#             TF-IDF    = TF × IDF
#               ↳ high score = word is frequent HERE but rare ELSEWHERE = meaningful signal.
#
# Result: a sparse dict {term: float} — the chunk's coordinate in vocabulary-space.
#
# Limitation: purely keyword-based. "car" and "automobile" are orthogonal dimensions.
# Production fix: use dense neural encoders (nomic-embed-text, text-embedding-3-small)
# trained on billions of examples so semantically similar text lands near each other.

class TFIDFVectorizer:
    def __init__(self) -> None: # constructor
        self.idf: dict[str, float] = {}
        self.corpus_size: int = 0

    # learns from the whole corpus(dir)
    def fit(self, corpus: list[str]) -> None:
        """Compute IDF weights over the full chunk corpus."""
        self.corpus_size = len(corpus) # dir
        df: Counter = Counter() # df=dictionary(hashmap: string → int) 
        for doc in corpus:
            # each term counted once per doc for IDF (not per occurrence)
            for token in set(tokenize(doc)):
                df[token] += 1
        self.idf = {
            term: math.log(self.corpus_size / (1 + freq)) + 1
            for term, freq in df.items()
        }

    # applies what was learned to a single input
    def transform(self, text: str) -> dict[str, float]:
        """Convert a single text to a TF-IDF sparse vector."""
        tokens = tokenize(text)
        if not tokens:
            return {}
        tf = Counter(tokens) # tf = unordered map<string, int>+ counting logic, 
        total = len(tokens)
        return {
            term: (count / total) * self.idf[term]
            for term, count in tf.items()
            if term in self.idf  # ignore OOV terms not seen during fit
        }

    def fit_transform(self, corpus: list[str]) -> list[dict[str, float]]:
        """Fit IDF on corpus, then vectorize every chunk."""
        self.fit(corpus)
        return [self.transform(doc) for doc in corpus]


# ── 5. Cosine Similarity ─────────────────────────────────────────────────────
# THEORY: Given two vectors A and B, cosine similarity measures the angle between
# them — i.e. whether they *point in the same direction*, regardless of length.
#
#   cos(θ) = (A · B) / (|A| × |B|)
#
#   = 1.0  → identical direction (perfectly similar vocabulary proportions)
#   = 0.0  → perpendicular (zero shared vocabulary)
#   (TF-IDF values are ≥ 0 so cos ∈ [0, 1])
#
# Why not Euclidean distance?
#   A long document has larger raw counts → a bigger magnitude vector.
#   It would appear "far" from a short query even if they cover the same topic.
#   Cosine normalizes for length — comparing *proportional composition*, not raw size.
#
# Sparse trick: only iterate over the intersection of non-zero terms.
# Dense production code uses numpy dot products for O(d) SIMD-accelerated math.

def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Cosine similarity between two TF-IDF sparse vectors in [0, 1]."""
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in vec_a if t in vec_b)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ── 6. In-Memory Vector Store ─────────────────────────────────────────────────
# THEORY: A vector store holds two parallel arrays per chunk:
#   • texts    → original strings returned as context to the LLM
#   • vectors  → embeddings used for similarity scoring
#   • metadata → provenance (source file, chunk index) for citation / debugging
#
# Retrieval here is brute-force: O(n) comparisons against every stored vector.
# That's fine for a few thousand chunks (< 10 ms). At millions of vectors,
# production systems use Approximate Nearest Neighbour (ANN) indexes:
#   HNSW (Hierarchical Navigable Small World) — graph-based, used by ChromaDB, Weaviate
#   IVF  (Inverted File Index) — cluster-then-search, used by FAISS, Pinecone
# ANN trades a tiny recall loss for O(log n) query time instead of O(n).

class VectorStore:
    def __init__(self) -> None:
        self.texts: list[str] = []
        self.vectors: list[dict[str, float]] = []
        self.metadata: list[dict] = []

    def add(self, text: str, vector: dict[str, float], meta: dict | None = None) -> None:
        self.texts.append(text)
        self.vectors.append(vector)
        self.metadata.append(meta or {})

#  __ mean it’s a special method that Python recognizes for built-in operations (like len(), str(), iter(), etc.).
    def __len__(self) -> int:
        return len(self.texts)


# ── 7. Retrieval: Top-K Nearest Neighbours ───────────────────────────────────
# THEORY: At query time:
#   1. Embed the question with the SAME vectorizer used during indexing.
#      CRITICAL: the query must live in the same vector space as the corpus.
#      Different IDF weights → different space → scores are meaningless.
#   2. Score every stored chunk: similarity(query_vec, chunk_vec).
#   3. Return the top-k highest-scoring chunks.
#
# Choosing N:
#   Too small (n=1) → may miss complementary information spread across chunns.
#   Too large (n=20) → LLM context fills with noise; cost/latency rises.
#   Typical production n: 3-5 for Q&A chat, 10-20 for summarization.
#
# Advanced retrieval:
#   • Hybrid search: combine dense (neural) + sparse (BM25/TF-IDF) scores.
#   • Re-ranking: a cross-encoder model re-scores the top-n for precision.
#   • HyDE: generate a hypothetical answer, embed it, retrieve — better recall.

def retrieve(
    query: str,
    store: VectorStore,
    vectorizer: TFIDFVectorizer,
    k: int = 3,
) -> list[tuple[float, str, dict]]:
    """Return [(score, text, meta), ...] sorted by descending cosine similarity."""
    query_vec = vectorizer.transform(query)
    # [] specifically means: give me all results now, in a list.
    scored = [
        (cosine_similarity(query_vec, vec), text, meta)
        for vec, text, meta in zip(store.vectors, store.texts, store.metadata)
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


# ── 8. Prompt Construction ────────────────────────────────────────────────────
# THEORY: Retrieved chunks become the *context window* injected into the LLM prompt.
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
    """Assemble a RAG prompt from the retrieved (score, text, meta) tuples."""
    context_parts = []
    for i, (score, text, meta) in enumerate(results, 1):
        source = meta.get("source", "?")
        context_parts.append(
            f"[Context {i}] source={source}  relevance={score:.3f}\n{text}"
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


# ── 9. Generation (mock) ──────────────────────────────────────────────────────
# THEORY: The assembled prompt is sent to an LLM which reads the context and
# generates a grounded, coherent answer. Common options:
#   Local:  Ollama → POST /api/chat  {"model": "gemma3:4b", "messages": [...]}
#   Cloud:  OpenAI → POST /v1/chat/completions
#           Anthropic → POST /v1/messages
#
# See production implementation in python-services/rag/main.py.
# This mock just displays the prompt so you can inspect exactly what the model
# would receive — the most important debugging tool in RAG development.

def generate(prompt: str) -> str:
    """Display the assembled prompt (swap for a real LLM HTTP call in production)."""
    border = "─" * 72
    lines = [
        f"\n{border}",
        " PROMPT SENT TO LLM",
        border,
        prompt,
        border,
        " ↑ Connect to Ollama / OpenAI / Anthropic here to get a real answer.",
        border,
    ]
    return "\n".join(lines)


# ── 10. Index Builder ─────────────────────────────────────────────────────────
# THEORY: Indexing (Load → Chunk → Embed → Store) happens ONCE (or on document update).
# It is expensive: embedding N chunks takes O(N × chunk_size) time.
# In production the index is persisted to disk / a vector DB so it survives restarts.
# Query time (Embed query → Retrieve → Generate) is cheap: one embedding + k dot products.

def build_index(docs_dir: str) -> tuple[VectorStore, TFIDFVectorizer, list[str]]:
    """Load .md files, chunk them, fit TF-IDF, and populate the vector store."""
    docs = load_documents(docs_dir)
    if not docs:
        raise FileNotFoundError(f"No .md files found in {docs_dir}")

    all_chunks: list[str] = []
    all_metas: list[dict] = []

    for filename, content in docs.items():
        for i, chunk in enumerate(chunk_text(content)):
            all_chunks.append(chunk)
            all_metas.append({"source": filename, "chunk_idx": i})

    print(f"[INDEX] {len(docs)} documents → {len(all_chunks)} chunks")

    vectorizer = TFIDFVectorizer()
    vectors = vectorizer.fit_transform(all_chunks)

    store = VectorStore()
    for chunk, vec, meta in zip(all_chunks, vectors, all_metas):
        store.add(chunk, vec, meta)

    print(f"[INDEX] Vocabulary: {len(vectorizer.idf)} unique terms")
    return store, vectorizer, list(docs.keys())


# ── 11. Query Interface ───────────────────────────────────────────────────────
# THEORY: At query time the steps are:
#   1. Embed the question (same vectorizer, same IDF weights — same vector space).
#   2. Retrieve top-k most similar chunks (nearest neighbours).
#   3. Assemble context → build prompt.
#   4. Send prompt to LLM → return answer.
# Latency budget in production: embedding ~5 ms, retrieval ~2 ms, LLM ~500-2000 ms.

def ask(question: str, store: VectorStore, vectorizer: TFIDFVectorizer, k: int = 3) -> str:
    """End-to-end: retrieve relevant chunks and build the LLM prompt."""
    print(f"\n[QUERY] {question!r}  (top-{k} chunks)")
    results = retrieve(question, store, vectorizer, k)

    print("[RETRIEVED]")
    for score, text, meta in results:
        preview = text[:90].replace("\n", " ")
        print(f"  {score:.3f}  {meta['source']}  \"{preview}...\"")

    prompt = build_prompt(question, results)
    return generate(prompt)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test and debug only the load_documents function
    import pprint
    DOCS_DIR = str(Path(__file__).parent)
    print(f"[DEBUG] Loading .md files from: {DOCS_DIR}")
    docs = load_documents(DOCS_DIR)
    print(f"[DEBUG] Found {len(docs)} .md files.")
    for fname, content in docs.items():
        print(f"\n[FILE] {fname} (first 120 chars):\n{content[:120]}\n{'-'*40}")
    # Use pprint to show the dictionary structure if needed
    # pprint.pprint(docs)
