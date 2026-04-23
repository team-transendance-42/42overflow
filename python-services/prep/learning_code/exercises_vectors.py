"""
=============================================================================
EXERCISES — Vectors(dynamic arr), Direction, Cosine Similarity
=============================================================================
"""
import math

# =============================================================================
# HELPERS
#=============================================================================

def magnitude(v: list[float]) -> float:
    return math.sqrt(sum(x**2 for x in v))

"""
zip(a, b)
Pairs elements from a and b together into tuples:
a = [1, 2, 3]
b = [4, 5, 6]
list(zip(a, b))  # [(1, 4), (2, 5), (3, 6)]
ai * bi for ai, bi in zip(a, b)

A generator expression that multiplies each pair:
(1*4, 2*5, 3*6) → (4, 10, 18)
sum(...)

Adds up the products: 4 + 10 + 18 = 32
edge cases:
a = [1, 2]
b = [3, 4, 5]
sum(ai * bi for ai, bi in zip(a, b))  # Only uses (1,3) and (2,4)
Empty lists: Returns 0.
Alternative (with NumPy for large arrays):
import numpy as np
np.dot(a, b)
"""
def dot_product(a: list[float], b: list[float]) -> float:
    return sum(ai * bi for ai, bi in zip(a, b))

def cosine_similarity(a: list[float], b: list[float]) -> float:
    mag_a, mag_b = magnitude(a), magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product(a, b) / (mag_a * mag_b)


# =============================================================================
# EXERCISE 1 — Compute magnitude by hand
# =============================================================================
# The magnitude of a vector is its "length" in space.
# Formula: sqrt( x1² + x2² + x3² + ... )
#
# Example: magnitude([3, 4]) = sqrt(9 + 16) = sqrt(25) = 5
#
# Task: compute the magnitude of each vector WITHOUT using the helper above.
# Use only math.sqrt() and basic arithmetic.

def exercise_1():
    v1 = [3.0, 4.0]          # expected: 5.0
    v2 = [1.0, 0.0]          # expected: 1.0  (already unit length)
    v3 = [1.0, 1.0]          # expected: sqrt(2) ≈ 1.4142
    v4 = [2.0, 3.0, 6.0]     # expected: 7.0

    # YOUR CODE — replace None with your calculation
    mag_v1 = None
    mag_v2 = None
    mag_v3 = None
    mag_v4 = None

    # check
    assert round(mag_v1, 4) == 5.0,             f"v1 wrong: got {mag_v1}"
    assert round(mag_v2, 4) == 1.0,             f"v2 wrong: got {mag_v2}"
    assert round(mag_v3, 4) == round(math.sqrt(2), 4), f"v3 wrong: got {mag_v3}"
    assert round(mag_v4, 4) == 7.0,             f"v4 wrong: got {mag_v4}"
    print("EXERCISE 1 passed ✓")


# =============================================================================
# EXERCISE 2 — Compute dot product by hand
# =============================================================================
# Dot product: multiply matching components, then sum everything.
# Formula: A·B = a1*b1 + a2*b2 + a3*b3 + ...
#
# Example: [1,2,3] · [4,5,6] = (1×4) + (2×5) + (3×6) = 4+10+18 = 32

def exercise_2():
    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]     # expected: 32.0

    c = [1.0, 0.0]
    d = [0.0, 1.0]           # expected: 0.0  (perpendicular axes)

    e = [3.0, 3.0]
    f = [3.0, 3.0]           # expected: 18.0 (same vector)

    # YOUR CODE — replace None
    dp_ab = None
    dp_cd = None
    dp_ef = None

    assert dp_ab == 32.0,  f"ab wrong: got {dp_ab}"
    assert dp_cd == 0.0,   f"cd wrong: got {dp_cd}"
    assert dp_ef == 18.0,  f"ef wrong: got {dp_ef}"
    print("EXERCISE 2 passed ✓")


# =============================================================================
# EXERCISE 3 — Cosine similarity formula
# =============================================================================
# cosine(A, B) = (A · B) / (|A| × |B|)
#
# Using dot_product() and magnitude() from the helpers above is fine here.
# Write the formula yourself — do NOT call cosine_similarity().

def my_cosine(a: list[float], b: list[float]) -> float:
    # YOUR CODE — replace this line
    return None


def exercise_3():
    # identical vectors → should be 1.0
    assert round(my_cosine([1.0, 0.0], [1.0, 0.0]), 4) == 1.0

    # perpendicular → should be 0.0
    assert round(my_cosine([1.0, 0.0], [0.0, 1.0]), 4) == 0.0

    # opposite → should be -1.0
    assert round(my_cosine([1.0, 0.0], [-1.0, 0.0]), 4) == -1.0

    # same direction, different magnitude → still 1.0
    assert round(my_cosine([1.0, 1.0], [100.0, 100.0]), 4) == 1.0

    print("EXERCISE 3 passed ✓")


# =============================================================================
# EXERCISE 4 — Prove that scaling does NOT change direction
# =============================================================================
# Key insight: [3, 4] and [6, 8] and [0.3, 0.4] all point the same direction.
# Cosine similarity between any two of them should be 1.0.
#
# Task: compute cosine similarity for all three pairs and confirm they are 1.0.
# This proves that MAGNITUDE doesn't matter, only DIRECTION does.

def exercise_4():
    v1 = [3.0,  4.0 ]
    v2 = [6.0,  8.0 ]    # v1 × 2
    v3 = [0.3,  0.4 ]    # v1 × 0.1

    # YOUR CODE — compute the three pairwise cosine similarities
    sim_12 = None   # between v1 and v2
    sim_13 = None   # between v1 and v3
    sim_23 = None   # between v2 and v3

    assert round(sim_12, 4) == 1.0, f"v1 vs v2: expected 1.0, got {sim_12}"
    assert round(sim_13, 4) == 1.0, f"v1 vs v3: expected 1.0, got {sim_13}"
    assert round(sim_23, 4) == 1.0, f"v2 vs v3: expected 1.0, got {sim_23}"
    print("EXERCISE 4 passed ✓  (scaling never changes direction)")


# =============================================================================
# EXERCISE 5 — Find the odd one out
# =============================================================================
# Four of these five vectors point in roughly the same direction.
# One is the "odd one out" — it points in a completely different direction.
#
# Task: find which index (0–4) is the odd one out.
# Do this by computing cosine similarity between every pair and finding
# the vector that scores low against all others.
# Return that index as an integer.

def exercise_5() -> int:
    vectors = [
        [0.9, 0.1, 0.05],   # 0
        [0.85, 0.15, 0.0],  # 1
        [0.88, 0.12, 0.02], # 2
        [0.05, 0.05, 0.95], # 3  ← odd one out (points in a completely different direction)
        [0.91, 0.09, 0.03], # 4
    ]

    # YOUR CODE
    # Hint: for each vector, compute the AVERAGE cosine similarity to all others.
    # The one with the lowest average is the odd one out.
    odd_index = None

    assert odd_index == 3, f"wrong: got {odd_index}, expected 3"
    print("EXERCISE 5 passed ✓")
    return odd_index


# =============================================================================
# EXERCISE 6 — Normalise a vector (make it unit length)
# =============================================================================
# A "unit vector" has magnitude = 1.0.
# You create one by dividing each component by the vector's magnitude.
#
# Formula: normalise(v) = v / |v|   (component-wise)
#
# Why this matters:
#   After normalisation, dot_product(a, b) == cosine_similarity(a, b)
#   Production vector DBs pre-normalise everything so they only need
#   a dot product (faster) instead of full cosine.

def normalise(v: list[float]) -> list[float]:
    # YOUR CODE — return a new list with each component divided by magnitude(v)
    return None


def exercise_6():
    v = [3.0, 4.0]
    n = normalise(v)

    # magnitude of a normalised vector must be exactly 1.0
    assert n is not None,                          "normalise() returned None"
    assert round(magnitude(n), 6) == 1.0,          f"magnitude should be 1.0, got {magnitude(n)}"
    assert round(n[0], 4) == round(3/5, 4),        f"component 0 wrong: {n[0]}"
    assert round(n[1], 4) == round(4/5, 4),        f"component 1 wrong: {n[1]}"

    # dot product of two normalised vectors == their cosine similarity
    a = normalise([1.0, 2.0, 3.0])
    b = normalise([4.0, 5.0, 6.0])
    assert round(dot_product(a, b), 6) == round(cosine_similarity(a, b), 6), \
        "dot product of normalised != cosine similarity"

    print("EXERCISE 6 passed ✓")


# =============================================================================
# EXERCISE 7 — Vector arithmetic encodes meaning
# =============================================================================
# In a good embedding space, you can do arithmetic with directions.
# Classic example: king - man + woman ≈ queen
#
# These toy 3D vectors have hand-crafted dimensions:
#   dim 0 = royalty score
#   dim 1 = gender (0 = male, 1 = female)
#   dim 2 = human score
#
# Task: compute (king - man + woman) and confirm the result is closer
# to 'queen' than to any other word in the vocabulary.

def exercise_7():
    vocab = {
        "king":   [0.9, 0.0, 0.9],
        "queen":  [0.9, 1.0, 0.9],
        "man":    [0.0, 0.0, 0.9],
        "woman":  [0.0, 1.0, 0.9],
        "castle": [0.8, 0.5, 0.0],  # royalty but not human
    }

    king, man, woman = vocab["king"], vocab["man"], vocab["woman"]

    # YOUR CODE — compute the analogy vector
    # analogy = king - man + woman  (component-wise arithmetic)
    analogy = None  # should be a list of 3 floats

    # YOUR CODE — find which word in vocab the analogy is closest to
    # Hint: compute cosine_similarity(analogy, vec) for each word, find the max
    closest_word = None  # should be the string "queen"

    assert analogy is not None, "analogy is None"
    assert closest_word == "queen", f"expected 'queen', got '{closest_word}'"
    print(f"EXERCISE 7 passed ✓  king - man + woman = '{closest_word}'")


# =============================================================================
# EXERCISE 8 — Build a search function
# =============================================================================
# Given a "database" of toy vectors and a query vector,
# return the top-k most similar items as a list of (similarity, label) tuples,
# sorted from most similar to least.

def vector_search(
    query: list[float],
    database: dict[str, list[float]],
    top_k: int = 3,
) -> list[tuple[float, str]]:
    """
    Compute cosine similarity between query and every vector in database.
    Return top_k results as [(similarity, label), ...] sorted descending.
    """
    # YOUR CODE
    return None


def exercise_8():
    db = {
        "cat":        [0.90, 0.10, 0.02],
        "dog":        [0.80, 0.20, 0.05],
        "kitten":     [0.88, 0.12, 0.01],
        "puppy":      [0.78, 0.22, 0.06],
        "database":   [0.02, 0.05, 0.95],
        "SQL":        [0.01, 0.03, 0.92],
        "index":      [0.03, 0.04, 0.90],
    }

    query = [0.89, 0.11, 0.02]   # clearly in the "animal" cluster

    results = vector_search(query, db, top_k=3)

    assert results is not None,          "vector_search returned None"
    assert len(results) == 3,            f"expected 3 results, got {len(results)}"

    # top result must be animal-like
    top_sim, top_label = results[0]
    assert top_label in {"cat", "kitten", "dog"}, \
        f"top result should be an animal, got '{top_label}'"

    # results must be sorted descending
    sims = [s for s, _ in results]
    assert sims == sorted(sims, reverse=True), "results not sorted by similarity"

    print(f"EXERCISE 8 passed ✓  top match for animal query: '{top_label}' ({top_sim:.4f})")


# =============================================================================
# EXERCISE 9 — Chunk a document
# =============================================================================
# Before embedding, long documents are split into overlapping chunks.
# Overlap prevents meaning from being cut off at boundaries.
#
# Task: implement chunk_text(text, chunk_size, overlap) that:
#   - splits text into a list of words
#   - yields chunks of `chunk_size` words
#   - each chunk starts `(chunk_size - overlap)` words after the previous one
#
# Example:
#   words = [A, B, C, D, E, F, G]
#   chunk_size=4, overlap=2
#   chunk 1: [A, B, C, D]          starts at index 0
#   chunk 2: [C, D, E, F]          starts at index 2  (4-2=2 step)
#   chunk 3: [E, F, G]             starts at index 4  (last chunk may be shorter)

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks. Returns list of chunk strings."""
    # YOUR CODE
    return None


def exercise_9():
    text = "A B C D E F G H I J"   # 10 words

    chunks = chunk_text(text, chunk_size=4, overlap=2)

    # step = chunk_size - overlap = 2, so starts: 0, 2, 4, 6, 8
    # last chunk at index 8 has only 2 words — that is correct, keep it
    assert chunks is not None,  "chunk_text returned None"
    assert chunks[0] == "A B C D",  f"chunk 0 wrong: '{chunks[0]}'"
    assert chunks[1] == "C D E F",  f"chunk 1 wrong: '{chunks[1]}'"
    assert chunks[2] == "E F G H",  f"chunk 2 wrong: '{chunks[2]}'"
    assert chunks[3] == "G H I J",  f"chunk 3 wrong: '{chunks[3]}'"
    assert len(chunks) == 5,        f"expected 5 chunks (incl. short tail), got {len(chunks)}"

    # overlap means consecutive chunks share words
    words_0 = chunks[0].split()
    words_1 = chunks[1].split()
    shared = set(words_0) & set(words_1)
    assert len(shared) == 2, f"expected 2 shared words, got {len(shared)}: {shared}"

    print("EXERCISE 9 passed ✓")


# =============================================================================
# EXERCISE 10 — Full mini RAG pipeline (no Ollama, toy vectors)
# =============================================================================
# Put everything together.
# You have a "knowledge base" of (text, vector) pairs.
# Given a query vector, retrieve the top-2 chunks, build an augmented prompt,
# and return it as a string.
#
# This is exactly what python-services/rag/main.py does — just with
# real vectors from Ollama instead of these toy ones.

def build_rag_prompt(
    query_text: str,
    query_vector: list[float],
    knowledge_base: list[tuple[str, list[float]]],
    top_k: int = 2,
) -> str:
    """
    1. Search knowledge_base for top_k most similar vectors to query_vector.
    2. Extract the text of those chunks.
    3. Return this string (fill in the blanks):

    Use the context below to answer. If context is missing, say you are unsure.

    Context:
    <chunk 1>
    ---
    <chunk 2>

    Question:
    <query_text>
    """
    # YOUR CODE
    return None


def exercise_10():
    kb = [
        ("The piscine is the 4-week selection bootcamp.",  [0.9, 0.1, 0.0]),
        ("42 has no teachers and no lectures.",             [0.85, 0.15, 0.0]),
        ("Projects are peer-reviewed by students.",         [0.8, 0.2, 0.0]),
        ("Docker is a container platform.",                 [0.0, 0.1, 0.9]),
        ("SQL is used to query relational databases.",      [0.0, 0.05, 0.95]),
    ]

    query_text   = "How does evaluation work at 42?"
    query_vector = [0.82, 0.18, 0.0]   # points toward the "42 school" cluster

    prompt = build_rag_prompt(query_text, query_vector, kb, top_k=2)

    assert prompt is not None,                       "returned None"
    assert "Context:" in prompt,                     "missing 'Context:'"
    assert "Question:" in prompt,                    "missing 'Question:'"
    assert query_text in prompt,                     "query text missing from prompt"
    assert "peer-reviewed" in prompt or "piscine" in prompt or "no teachers" in prompt, \
        "retrieved chunks should be about 42, not Docker/SQL"

    print("EXERCISE 10 passed ✓")
    print("\nGenerated prompt:")
    print("-" * 50)
    print(prompt)


# =============================================================================
# RUN ALL
# =============================================================================

def run_all():
    print("Running exercises...\n")
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()
    exercise_7()
    exercise_8()
    exercise_9()
    exercise_10()
    print("\nAll exercises done.")

if __name__ == "__main__":
    run_all()
