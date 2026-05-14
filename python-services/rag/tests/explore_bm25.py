"""
Run: uv run python -m tests.explore_bm25
No services required — pure in-memory math.

Walks through BM25+ internals step by step so you can see exactly
what happens to your documents and query at each stage.
"""
from bm25_index import BM25Index, _tokenize

DOCS = [
    "Q: What is free()?\nA: Releases heap memory.",
    "Q: What is malloc()?\nA: Allocates heap memory.",
    "Q: What causes a segfault?\nA: Dereferencing a null pointer.",
]
IDS   = ["free-1", "malloc-2", "seg-3"]
QUERY = "heap memory allocation"

SEP = "─" * 60


def show_bm25_internals():
    idx = BM25Index()
    idx.build(DOCS, IDS)
    bm25 = idx._bm25  # access rank_bm25 internals directly

    # ── STEP 1: tokenization ─────────────────────────────────────────
    print(f"\n{SEP}")
    print("STEP 1 — document tokenization")
    print(SEP)
    for id_, doc in zip(IDS, DOCS):
        tokens = _tokenize(doc)
        print(f"  {id_:10s}  {tokens}") # :10s: format as a string (s), right-pad with spaces to a width of 10 characters

    # ── STEP 2: corpus stats ─────────────────────────────────────────
    print(f"\n{SEP}")
    print("STEP 2 — corpus stats")
    print(SEP)
    print(f"  docs     : {bm25.corpus_size}")
    print(f"  avg len  : {bm25.avgdl:.1f} tokens")
    doc_lengths = bm25.doc_len
    for id_, length in zip(IDS, doc_lengths):
        print(f"  {id_:10s}  {length} tokens")

    # ── STEP 3: IDF per term in query ────────────────────────────────
    print(f"\n{SEP}")
    print("STEP 3 — IDF for each query token")
    print(SEP)
    print(f"  query: {QUERY!r}") # !r: format using repr(esent), which adds quotes around the string and escapes special characters, making it clear that it's a string literal in the output
    query_tokens = _tokenize(QUERY)
    print(f"  tokens: {query_tokens}\n")
    print(f"  {'token':20s}  {'in docs':30s}  {'IDF':>8s}") # > here means right-align the text in a field of width 8 characters, s means it's a string; default is left align
    print(f"  {'─'*20}  {'─'*30}  {'─'*8}")
    for token in query_tokens:
        idf = bm25.idf.get(token, 0.0) # if missing assingn 0.0, which means the token is not in the vocabulary at all (never appeared in any document), so it contributes nothing to the score.
        in_docs = [id_ for id_, freq in zip(IDS, bm25.doc_freqs) if freq.get(token, 0) > 0]
        in_str  = ", ".join(in_docs) if in_docs else "(none — not in vocabulary)"
        print(f"  {token:20s}  {in_str:30s}  {idf:8.4f}")
    print()
    print("  IDF intuition: higher = rarer across docs = more signal.")
    print("  BM25+ IDF stays positive even for common terms (unlike Okapi).")

    # ── STEP 4: per-doc score breakdown ──────────────────────────────
    print(f"\n{SEP}")
    print("STEP 4 — per-document score breakdown")
    print(SEP)
    print(f"  k1={bm25.k1}  b={bm25.b}  delta={bm25.delta}  avgdl={bm25.avgdl:.1f}\n")

    for i, (id_, doc_freq, doc_len) in enumerate(zip(IDS, bm25.doc_freqs, doc_lengths)):
        print(f"  [{id_}]  doc_len={doc_len}")
        total = 0.0
        for token in query_tokens:
            idf = bm25.idf.get(token, 0.0)
            tf  = doc_freq.get(token, 0)
            if idf == 0.0:
                print(f"    {token:20s}  tf={tf}  idf=0.0000  → not in vocab, skip")
                continue
            # BM25+ formula:
            # score += IDF × (delta + tf×(k1+1) / (tf + k1×(1 - b + b×dl/avgdl)))
            norm     = bm25.k1 * (1 - bm25.b + bm25.b * doc_len / bm25.avgdl)
            tf_score = bm25.delta + tf * (bm25.k1 + 1) / (tf + norm)
            contrib  = idf * tf_score
            total   += contrib
            print(f"    {token:20s}  tf={tf}  idf={idf:.4f}  "
                  f"tf_score={tf_score:.4f}  contrib={contrib:+.4f}")
        print(f"    {'TOTAL':20s}  {total:.4f}\n")

    # ── STEP 5: final ranking ────────────────────────────────────────
    print(f"\n{SEP}")
    print("STEP 5 — final ranked results")
    print(SEP)
    results = idx.search(QUERY, n=len(DOCS))
    if not results:
        print("  (no results — all scores were 0)")
    for rank, r in enumerate(results):
        print(f"  #{rank+1}  score={r['score']:.4f}  {r['id']}")

    print(f"\n{SEP}\n")


if __name__ == "__main__":
    show_bm25_internals()
