"""
=============================================================================
                                EMBEDDINGS
=============================================================================

Run individual sections by uncommenting the main() call at the bottom.
Requirements: pip install numpy requests
Ollama must be running for sections 5+: docker compose up ollama
to start with:
cd /home/pskpe/42overflow/python-services/prep/learning_code
python3 embeddings_tutorial.py
=============================================================================
"""

import math
import json
import urllib.request  # stdlib only — no extra install needed for HTTP

# =============================================================================
# SECTION 1 — What is a Vector?
# =============================================================================
# dynamic arr: Every number is called a "component" or "dimension".
# python3 python-services/prep/learning_code/embeddings_tutorial.py
def section_1_what_is_a_vector():
    print("\n" + "="*60)
    print("SECTION 1 — What is a Vector?")
    print("="*60)

    # A 2D vector: two numbers describing a point in a plane
    vec_2d = [3.0, 4.0]
    print(f"2D vector: {vec_2d}")
    print(f"It points to x={vec_2d[0]}, y={vec_2d[1]} in 2D space")

    # The "magnitude" (length of hypotenuse)
    # Pythagorean theorem: hypotenuse = sqrt(3² + 4²)shorter sides = sqrt(9 + 16) = sqrt(25) = 5 hypothenose/magnitude
    magnitude = math.sqrt(sum(x**2 for x in vec_2d))
    print(f"Magnitude (length) of {vec_2d}: {magnitude}")

    # In real embeddings the dimension is 768, 1024, or 1536 — same concept,
    # just way more numbers. "nomic-embed-text" produces 768-dim vectors.
    fake_768_dim_vector = [0.0] * 768 # It creates a list with 768 zeros in one line.
    fake_768_dim_vector[0] = 0.12
    fake_768_dim_vector[5] = -0.45
    fake_768_dim_vector[42] = 0.89
    print(f"\nA 768-dim vector (showing 3 of 768 components):")
    print(f"  [0]:  {fake_768_dim_vector[0]}")
    print(f"  [5]:  {fake_768_dim_vector[5]}")
    print(f"  [42]: {fake_768_dim_vector[42]}")
    print(f"  ... (765 more components)")


# =============================================================================
# SECTION 2 — Why Not Just Compare Words?
# =============================================================================
#
# PROBLEM: traditional string comparison fails for semantics.
#
# "car" == "automobile"    → False   (but same meaning!)
# "bank" == "bank"         → True    (but bank the river or bank the money?)
#
# Classic "bag of words" approach: count word occurrences.
# "the cat sat" → { "the":1, "cat":1, "sat":1 }
# "the feline rested" → { "the":1, "feline":1, "rested":1 }
# Overlap = only "the" → 33% similarity. These sentences mean the SAME thing!
#
# Embeddings fix this: they encode MEANING, not words.

def section_2_why_not_words():
    print("\n" + "="*60)
    print("SECTION 2 — Why Not Just Compare Words?")
    print("="*60)

    def bag_of_words(text: str) -> dict:
        """Counts each word. Ignores order and meaning.""" # Python stores it as the function's __doc__ attribute; """...""" — actual string, stored in memory; It's not a file — it's an attribute on the function object in memory. Tools like help() read it
        counts = {} # dict(like js map)
        for word in text.lower().split():
            counts[word] = counts.get(word, 0) + 1 # get curr count of the word, if none, put 0 and + 1
        return counts

    def bag_similarity(text_a: str, text_b: str) -> float:
        """Jaccard similarity of two bags of words."""
        a = set(bag_of_words(text_a).keys()) # dynamic arr, no dubs
        b = set(bag_of_words(text_b).keys())
        if not a and not b: # if a is empty  AND  b is empty
            return 1.0
        return len(a & b) / len(a | b)  # & intersection(keeps only what's in BOTH) / union(returns new container with both sets(no dubs0/arrs)

    pairs = [
        ("the cat sat on the mat", "the feline rested on the rug"),
        ("python is a programming language", "python is a snake"),
        ("I love coffee", "I love coffee"),
        ("machine learning is hard", "machine learning is hard"),
    ]

    print("\nBag-of-words similarity (ignores meaning):")
    for a, b in pairs:
        sim = bag_similarity(a, b)
        print(f"  '{a}'\n  '{b}'\n  → {sim:.2f}\n")

    print("Notice: 'cat sat on mat' vs 'feline rested on rug' scores low")
    print("even though they mean the same thing.")
    print("Embeddings would score them HIGH because they encode meaning.")


# =============================================================================
# SECTION 3 — Cosine Similarity From Scratch
# =============================================================================
#
# How do we compare two vectors to see if they mean the same thing?
# Answer: measure the ANGLE between them.
#
# If two vectors point in the same direction → angle = 0° → similarity = 1.0
# If they are perpendicular             → angle = 90° → similarity = 0.0
# If they point opposite directions     → angle = 180° → similarity = -1.0
#
# The formula (no library needed):
#
#   cosine_similarity(A, B) = (A · B) / (|A| × |B|)
#
# where:
#   A · B  = dot product = sum(a_i * b_i for each dimension i)
#   |A|    = magnitude of A = sqrt(sum(a_i²))
#
# WHY cosine and not Euclidean distance?
# Because we care about DIRECTION (meaning), not LENGTH (how much text).
# "Dog" and "A big fluffy dog" should be similar — cosine handles this.
# Euclidean distance would penalize the longer text.

def dot_product(a: list[float], b: list[float]) -> float:
    """Sum of element-wise products."""
    return sum(ai * bi for ai, bi in zip(a, b))

def magnitude(v: list[float]) -> float:
    """Length of the vector."""
    return math.sqrt(sum(x**2 for x in v))

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Cosine similarity between two vectors.
    Returns: float in [-1, 1]. Higher = more similar.
    """
    mag_a = magnitude(a)
    mag_b = magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product(a, b) / (mag_a * mag_b)

def section_3_cosine_similarity():
    print("\n" + "="*60)
    print("SECTION 3 — Cosine Similarity From Scratch")
    print("="*60)

    # Toy 3D vectors (imagine these are embeddings in 3 dimensions)
    # In reality your embedding model produces 768 dimensions — same math.
    vectors = {
        "cat":        [0.9, 0.1, 0.05],   # animal cluster
        "kitten":     [0.85, 0.15, 0.05],  # animal cluster (very close to cat)
        "dog":        [0.8, 0.2, 0.1],     # animal cluster (close)
        "database":   [0.05, 0.05, 0.95],  # tech cluster
        "SQL":        [0.02, 0.08, 0.92],  # tech cluster (close to database)
    }

    pairs = [
        ("cat", "kitten"),    # should be very high
        ("cat", "dog"),       # should be high
        ("cat", "database"),  # should be low
        ("database", "SQL"),  # should be high
        ("kitten", "SQL"),    # should be low
    ]

    print("\nCosine similarity between toy 3D vectors:")
    print(f"{'Pair':<30} {'Similarity':>10}  {'Interpretation'}")
    print("-" * 65)
    for a, b in pairs:
        sim = cosine_similarity(vectors[a], vectors[b])
        interpretation = "very similar" if sim > 0.98 else \
                         "similar" if sim > 0.90 else \
                         "somewhat related" if sim > 0.75 else "unrelated"
        print(f"  {a} vs {b:<20} {sim:.4f}      {interpretation}")

    print("\nFormula breakdown for 'cat' vs 'kitten':")
    a, b = vectors["cat"], vectors["kitten"]
    dp = dot_product(a, b)
    ma, mb = magnitude(a), magnitude(b)
    print(f"  A = {a}")
    print(f"  B = {b}")
    print(f"  Dot product A·B = {dp:.4f}")
    print(f"  |A| = {ma:.4f},  |B| = {mb:.4f}")
    print(f"  cosine = {dp:.4f} / ({ma:.4f} × {mb:.4f}) = {dp/(ma*mb):.4f}")


# =============================================================================
# SECTION 4 — How an Embedding Model Works (Intuition)
# =============================================================================
#
# An embedding model is a neural network (specifically a Transformer) that:
#
# 1. TOKENIZES the input:   "Hello world" → [15496, 995]  (token IDs)
#
# 2. LOOKS UP embeddings:   each token ID → a 768-dim vector (from a learned table)
#
# 3. RUNS TRANSFORMER LAYERS:
#    Each layer lets tokens "attend" to each other — "bank" next to "river"
#    vs "bank" next to "account" will produce different vectors after attention.
#    This is how context changes meaning.
#
# 4. POOLS to one vector:
#    The N token vectors → 1 vector for the whole sentence.
#    Common methods: mean pooling (average all tokens), CLS token (special token).
#
# 5. OUTPUT: a single 768-dim float vector that encodes the full meaning.
#
# The model was TRAINED to put similar-meaning sentences close together
# in this 768-dim space using contrastive learning:
#   - "cat" and "kitten" were given as a positive pair → pushed together
#   - "cat" and "database" were given as a negative pair → pushed apart
#
# After training on billions of such pairs, the geometry of the space
# encodes human language semantics.

def section_4_how_embedding_model_works():
    print("\n" + "="*60)
    print("SECTION 4 — How an Embedding Model Works (Intuition)")
    print("="*60)
    print("""
Steps inside nomic-embed-text (or any BERT-style model):

  Input text: "The piscine is a 4-week selection process"
       ↓
  [Tokenizer]
  "The" "pi" "##scine" "is" "a" "4" "-" "week" "selection" "process"
  → token IDs: [1996, 16576, 14107, 2003, 1037, ...]
       ↓
  [Token Embedding Lookup]
  Each token ID → a 768-dim vector from a learned table (vocab size ~30k)
       ↓
  [12 Transformer Layers]
  Each layer: self-attention + feed-forward network
  Tokens "see" each other → context changes their vectors
       ↓
  [Mean Pooling]
  Average all token vectors → one 768-dim vector
       ↓
  Output: [0.031, -0.124, 0.887, 0.003, ...]  (768 floats)

Why 768? That's the hidden size chosen when training the model.
Larger models use 1024 or 1536. More dimensions = more nuance,
but also more memory and slower similarity search.
""")


# =============================================================================
# SECTION 5 — Calling nomic-embed-text via Ollama (Real Embeddings)
# =============================================================================
#
# In this project, Ollama runs as a Docker service.
# The embed endpoint is: POST http://ollama:11434/api/embed
# (or http://localhost:11434/api/embed when testing locally)
#
# Request body:
# {
#   "model": "nomic-embed-text",
#   "input": ["text1", "text2", ...]   ← list of texts to embed
# }
#
# Response:
# {
#   "embeddings": [[0.031, -0.124, ...], [0.005, 0.91, ...]]
# }
# One vector per input text.

OLLAMA_URL = "http://localhost:11434"   # change to http://ollama:11434 in Docker

def embed_texts(texts: list[str], model: str = "nomic-embed-text") -> list[list[float]]:
    """
    Call Ollama's /api/embed endpoint.
    Returns a list of float vectors, one per input text.
    """
    payload = json.dumps({
        "model": model,
        "input": texts,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Ollama may return "embeddings" (list) or legacy "embedding" (single)
    if "embeddings" in data and data["embeddings"]:
        return data["embeddings"]
    if "embedding" in data and data["embedding"]:
        return [data["embedding"]]

    raise ValueError(f"No embeddings in response: {data}")


def section_5_real_embeddings():
    print("\n" + "="*60)
    print("SECTION 5 — Real Embeddings via Ollama")
    print("="*60)
    print("(Requires Ollama running + nomic-embed-text pulled)")
    print(f"Connecting to: {OLLAMA_URL}\n")

    texts = [
        "The piscine is a 4-week selection process at 42",
        "The swimming pool at school is for sport",  # 'piscine' is French for pool
        "Python is a programming language",
        "A python is a large non-venomous snake",
        "Machine learning helps computers learn from data",
        "Deep learning uses neural networks with many layers",
    ]

    try:
        print("Embedding 6 sentences...")
        vectors = embed_texts(texts)
        print(f"Got {len(vectors)} vectors, each of dimension {len(vectors[0])}\n")

        print("Pairwise cosine similarities (real semantic distances):")
        print(f"{'Pair':<70} {'Sim':>6}")
        print("-" * 78)

        # Compare every pair
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = cosine_similarity(vectors[i], vectors[j])
                label_i = texts[i][:32].ljust(33)
                label_j = texts[j][:32].ljust(33)
                print(f"  {label_i} | {label_j} → {sim:.4f}")

        print("\nExpected: '42 piscine' and 'swimming pool' score higher than")
        print("'42 piscine' and 'Python programming' — real model shows this.")

    except Exception as e:
        print(f"Could not reach Ollama: {e}")
        print("Start it with: docker compose up ollama")
        print("Then pull the model: docker exec <ollama_container> ollama pull nomic-embed-text")


# =============================================================================
# SECTION 6 — Building a Tiny In-Memory Vector Search Engine
# =============================================================================
#
# This is the core of what ChromaDB does — we build a minimal version
# from scratch so you understand exactly what happens inside.
#
# Steps:
#  1. Store (text, vector) pairs in a list
#  2. At query time: embed the query, compute cosine similarity vs all stored,
#     sort descending, return top-K
#
# ChromaDB and Qdrant do the same thing, but with:
#  - Persistent disk storage
#  - ANN (Approximate Nearest Neighbor) indices for speed on millions of vectors
#  - Metadata filtering
#  - HNSW or IVF indexing algorithms

class TinyVectorStore:
    """
    A minimal in-memory vector store.
    Educational only — does NOT scale beyond a few thousand documents.
    ChromaDB/Qdrant use ANN indices (HNSW) instead of brute-force scan.
    """

    def __init__(self):
        self._store: list[tuple[str, list[float]]] = []
        # Each entry is (original_text, embedding_vector)

    def add(self, texts: list[str], vectors: list[list[float]]) -> None:
        """Store text + its vector."""
        for text, vec in zip(texts, vectors):
            self._store.append((text, vec))

    def search(self, query_vector: list[float], top_k: int = 3) -> list[tuple[float, str]]:
        """
        Brute-force: compute cosine similarity vs EVERY stored vector.
        O(n × d) where n = number of stored docs, d = dimensions.
        Fine for hundreds of docs. Use ANN for millions.
        """
        scores = []
        for text, stored_vec in self._store:
            sim = cosine_similarity(query_vector, stored_vec)
            scores.append((sim, text))

        # Sort by similarity descending
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]


def section_6_tiny_vector_store():
    print("\n" + "="*60)
    print("SECTION 6 — Building a Tiny In-Memory Vector Search Engine")
    print("="*60)
    print("(Requires Ollama — skip if not running)\n")

    knowledge_base = [
        "The piscine is the 4-week intensive selection bootcamp at 42.",
        "42 is a coding school with no teachers, no lectures, and no tuition fees.",
        "Projects at 42 are peer-reviewed by other students using the moulinette.",
        "The common core at 42 consists of mandatory projects everyone must complete.",
        "Students work in clusters, which are large open workspaces with iMacs.",
        "Python was created by Guido van Rossum and first released in 1991.",
        "JavaScript is the primary language of web browsers.",
        "Docker containers package an application with all its dependencies.",
        "A vector database stores embeddings and performs fast similarity search.",
        "ChromaDB is an open-source embedding database written in Python.",
    ]

    try:
        print(f"Indexing {len(knowledge_base)} documents...")
        doc_vectors = embed_texts(knowledge_base)

        store = TinyVectorStore()
        store.add(knowledge_base, doc_vectors)
        print(f"Stored {len(knowledge_base)} vectors in TinyVectorStore\n")

        queries = [
            "What is the selection process at 42?",
            "How are projects graded?",
            "What is a vector database?",
            "Tell me about Docker",
        ]

        for query in queries:
            print(f"Query: '{query}'")
            [query_vec] = embed_texts([query])
            results = store.search(query_vec, top_k=2)
            for sim, text in results:
                print(f"  [{sim:.4f}] {text[:70]}")
            print()

        print("This is exactly what ChromaDB does — just persisted to disk")
        print("and with HNSW indexing instead of brute-force linear scan.")

    except Exception as e:
        print(f"Could not reach Ollama: {e}")
        print("(Set OLLAMA_URL to your running instance and retry)")


# =============================================================================
# SECTION 7 — ANN vs Brute Force: Why Production DBs Are Fast
# =============================================================================
#
# Problem with brute-force scan:
#   1M documents × 768 dimensions = 768M multiplications per query.
#   At 1ns per op → 768ms just for one query. Too slow.
#
# Solution: Approximate Nearest Neighbor (ANN) algorithms.
#
# HNSW (Hierarchical Navigable Small World) — used by ChromaDB, Qdrant:
#   - Builds a graph where similar vectors are connected
#   - Traversal finds approximate nearest neighbors in O(log n)
#   - "Approximate" means it may miss some results, but 99.9%+ accurate
#   - Typical latency: <1ms even for 1M vectors
#
# IVF (Inverted File Index) — used by Faiss:
#   - Clusters all vectors into K groups (k-means)
#   - At query time: only scan the nearest cluster(s), not all vectors
#   - Much faster than brute force, slight quality trade-off
#
# In practice (for this project):
#   ChromaDB handles all of this internally.
#   You just call /api/v1/collections/{name}/query and it returns top-K.

def section_7_ann_intuition():
    print("\n" + "="*60)
    print("SECTION 7 — Why Vector Search is Fast (ANN Intuition)")
    print("="*60)
    print("""
Brute-force linear scan: O(n × d)

  n=1,000,000 docs × d=768 dims = 768,000,000 multiplications
  At 1 billion ops/sec → ~768ms per query

HNSW graph traversal: O(log n × d)

  log₂(1,000,000) ≈ 20 hops × 768 dims = 15,360 multiplications
  At 1 billion ops/sec → ~0.015ms per query  (50,000× faster)

How HNSW works (simplified):
  - Layer 0: all vectors, densely connected to neighbors
  - Layer 1: random subset, connected to neighbors
  - Layer 2: smaller random subset
  - ...

  Query: start at top layer (sparse), greedily navigate toward
         the query vector, drop to lower layer, repeat.
         Like a skip list but in high-dimensional space.

ChromaDB uses HNSW internally.
You never call it directly — just POST /api/v1/collections/{name}/query
and it returns the top-K approximate nearest neighbors.
""")


# =============================================================================
# SECTION 8 — What "Dimensions" Actually Represent
# =============================================================================
#
# No one fully knows what each dimension encodes — the model learns it.
# But researchers have found that groups of dimensions tend to encode:
#
#   dims ~0-50:   syntactic features (is this a noun? a verb? tense?)
#   dims ~50-200: broad semantic categories (animal? tech? action?)
#   dims ~200-500: finer semantic distinctions
#   dims ~500-768: context-specific and idiomatic meaning
#
# This is why 768 dimensions is better than 50 — more capacity for nuance.
# But more dimensions = more memory and slower search.
#
# A key property: "linear relationships" exist in embedding space.
#
#   king - man + woman ≈ queen     (classic word2vec example)
#
# This means the direction in space encodes semantic relationships.
# "Adding the gender direction" to "king" gives "queen".
# These relationships emerge from training on language patterns.

def section_8_dimensions():
    print("\n" + "="*60)
    print("SECTION 8 — What Dimensions Actually Represent")
    print("="*60)
    print("""
Toy demonstration of linear relationships in embedding space.

If we had perfect 3D embeddings where:
  dim 0 = royalty score
  dim 1 = gender score  (0=male, 1=female)
  dim 2 = human score

Then:
  king   = [0.9, 0.0, 0.9]
  queen  = [0.9, 1.0, 0.9]
  man    = [0.0, 0.0, 0.9]
  woman  = [0.0, 1.0, 0.9]

  king - man + woman = [0.9,0.0,0.9] - [0.0,0.0,0.9] + [0.0,1.0,0.9]
                     = [0.9, 1.0, 0.9]   ← that's queen!

Real embeddings have 768 dimensions, not 3, and no dimension has a
clean human-readable label. But the same linear structure exists.
""")
    # Toy demonstration
    king  = [0.9, 0.0, 0.9]
    man   = [0.0, 0.0, 0.9]
    woman = [0.0, 1.0, 0.9]
    queen = [0.9, 1.0, 0.9]

    analogy = [king[i] - man[i] + woman[i] for i in range(3)]
    sim_to_queen = cosine_similarity(analogy, queen)
    sim_to_king  = cosine_similarity(analogy, king)

    print(f"king - man + woman = {analogy}")
    print(f"Cosine similarity to 'queen': {sim_to_queen:.4f}")
    print(f"Cosine similarity to 'king':  {sim_to_king:.4f}")
    print("→ result is closer to 'queen' than to 'king'")


# =============================================================================
# SECTION 9 — Normalisation and Why It Matters
# =============================================================================
#
# A "unit vector" has magnitude = 1. You get it by dividing by the magnitude.
# This is called "L2 normalisation".
#
# WHY NORMALISE?
# Without normalisation, a long document produces a large-magnitude vector
# and a short document produces a small one.
# Cosine similarity divides by magnitude — so it's already scale-invariant.
# BUT: many ANN libraries (Faiss, Qdrant) offer an optimised mode where
# all vectors are pre-normalised, so dot product = cosine similarity.
# This makes inner product search as accurate as cosine search, but faster.
#
# ChromaDB handles this for you. But you need to know it exists when you
# work with raw vector math or switch to Qdrant/Faiss.

def normalise(v: list[float]) -> list[float]:
    """L2 normalise: divide each component by the vector's magnitude."""
    mag = magnitude(v)
    if mag == 0:
        return v
    return [x / mag for x in v]

def section_9_normalisation():
    print("\n" + "="*60)
    print("SECTION 9 — Normalisation")
    print("="*60)

    short_doc = [0.2, 0.1, 0.9]           # small vector
    long_doc  = [4.0, 2.0, 18.0]          # same direction, 20× magnitude

    print(f"short_doc = {short_doc}  magnitude={magnitude(short_doc):.3f}")
    print(f"long_doc  = {long_doc}  magnitude={magnitude(long_doc):.3f}")
    print(f"\nCosine similarity (unnormalised): {cosine_similarity(short_doc, long_doc):.4f}")

    short_norm = normalise(short_doc)
    long_norm  = normalise(long_doc)
    print(f"\nAfter L2 normalisation:")
    print(f"  short_norm: {[round(x,4) for x in short_norm]}")
    print(f"  long_norm:  {[round(x,4) for x in long_norm]}")
    print(f"  They are identical! (same direction, now same magnitude)")
    print(f"\nDot product of normalised vectors = cosine similarity: "
          f"{dot_product(short_norm, long_norm):.4f}")
    print("This is why ANN libraries can use dot product instead of full cosine.")


# =============================================================================
# SECTION 10 — Putting It Together: Mini RAG From Scratch
# =============================================================================
#
# No libraries. Pure Python + one HTTP call to Ollama.
# This is conceptually identical to what python-services/rag/main.py does.

def section_10_mini_rag():
    print("\n" + "="*60)
    print("SECTION 10 — Mini RAG From Scratch (No Libraries)")
    print("="*60)
    print("(Requires Ollama with nomic-embed-text + gemma3:4b)\n")

    # --- INGESTION PHASE ---
    documents = [
        "The piscine is a 4-week intensive selection bootcamp at 42.",
        "42 is a coding school with no teachers and no tuition fees.",
        "Projects are peer-reviewed by other students using the moulinette.",
        "The common core consists of mandatory projects everyone must complete.",
        "Students work in clusters — large open workspaces with iMacs.",
    ]

    def call_ollama_chat(prompt: str, model: str = "gemma3:4b") -> str:
        payload = json.dumps({
            "model": model,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("message", {}).get("content", "").strip()

    try:
        print("Phase A: Ingestion")
        print(f"  Embedding {len(documents)} documents...")
        doc_vectors = embed_texts(documents)
        store = TinyVectorStore()
        store.add(documents, doc_vectors)
        print(f"  Stored {len(documents)} vectors.\n")

        question = "How are student projects evaluated?"
        print(f"Phase B: Query — '{question}'")

        # Step 1: embed the question
        [q_vec] = embed_texts([question])
        print("  Embedded question.")

        # Step 2: retrieve top-2 most relevant chunks
        results = store.search(q_vec, top_k=2)
        contexts = [text for _, text in results]
        print(f"  Retrieved {len(contexts)} chunks:")
        for sim, text in results:
            print(f"    [{sim:.4f}] {text}")

        # Step 3: build augmented prompt
        context_text = "\n---\n".join(contexts)
        prompt = (
            "Use the context below to answer. "
            "If context is missing, say you are unsure.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question:\n{question}"
        )
        print(f"\n  Augmented prompt:\n  {'-'*40}")
        print(f"  {prompt[:300]}...")
        print(f"  {'-'*40}\n")

        # Step 4: generate
        print("  Calling Ollama (gemma3:4b)...")
        answer = call_ollama_chat(prompt)
        print(f"\n  Answer:\n  {answer}\n")

    except Exception as e:
        print(f"Could not reach Ollama: {e}")
        print("Run: docker compose up ollama")


# =============================================================================
# MAIN — run all sections
# =============================================================================

def main():
#    section_1_what_is_a_vector()
     section_2_why_not_words()
#     section_3_cosine_similarity()
#     section_4_how_embedding_model_works()
#     section_5_real_embeddings()      # needs Ollama
#     section_6_tiny_vector_store()    # needs Ollama
#     section_7_ann_intuition()
#     section_8_dimensions()
#     section_9_normalisation()
#     section_10_mini_rag()            # needs Ollama

if __name__ == "__main__":
#     # Run sections that need no external dependencies (1-4, 7-9):
    #section_1_what_is_a_vector()
    section_2_why_not_words()
#     section_3_cosine_similarity()
#     section_4_how_embedding_model_works()
#     section_7_ann_intuition()
#     section_8_dimensions()
#     section_9_normalisation()

    # Uncomment when Ollama is running:
    # section_5_real_embeddings()
    # section_6_tiny_vector_store()
    # section_10_mini_rag()
