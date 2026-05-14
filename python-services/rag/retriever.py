"""
Hybrid retrieval: dense (ChromaDB cosine) + sparse (BM25+) merged with RRF.

Why two retrievers?
  Dense (nomic-embed-text): catches semantic similarity — "freeing memory"
    matches docs about free(), malloc(), heap corruption even without those
    exact words. Weak on exact tokens like ft_printf, %d, NULL.
  Sparse (BM25+): catches exact keyword matches — ft_printf, NULL, errno
    score high when those tokens appear verbatim. Blind to synonyms.
  RRF(reciprocal rank fusion) merge: combines both ranked lists by position, not score magnitude,
    so the incompatible numeric ranges don't matter.

This module is stateless — takes all inputs as parameters, returns results.
The caller (router.py) injects the BM25 index and id_to_text lookup.
"""
from collections import defaultdict # automatically creates a default value for any missing key, using provided func. d = defaultdict(int)
# d['a'] += 1  # No KeyError, 'a' is created with value 0, then incremented to 1  print(d['a'])  # 1

from bm25_index import BM25Index
from embedder   import embed_texts
from store      import query_dense

_RRF_K = 60  # standard constant — dampens rank-1 dominance


async def hybrid_search( question: str, bm25_index: BM25Index, id_to_text: dict[str, str], top_k: int = 5, ) -> list[dict]:
    """
    Run dense + sparse retrieval and merge results with RRF.

    Args:
        question:   raw user question string
        bm25_index: built BM25Index from startup (qa_cache["bm25"])
        id_to_text: {doc_id: formatted_text} for all QA pairs
        top_k:      number of results to return after merging

    Returns:
        [{"id": ..., "text": ..., "rrf_score": ...}, ...]
        sorted by descending rrf_score (best match first)
    """
    # 1. Dense search: embed question, find nearest vectors in ChromaDB.
    #    embed_texts returns list[list[float]] — we send one question,
    #    so we take index [0] to get the single embedding vector.
    question_embedding = (await embed_texts([question]))[0]
    dense_hits = query_dense(question_embedding, n=20)

    # 2. Sparse search: BM25+ keyword scoring in RAM, no I/O.
    sparse_hits = bm25_index.search(question, n=20)

    # 3. RRF merge: score each doc by its rank position in each list.
    #    rank 0 (best) → 1/(0+60) = 0.0167
    #    rank 19 (worst in top-20) → 1/(19+60) = 0.0127
    #    A doc ranked top-5 in both lists beats a doc ranked #1 in one list only.
    rrf_scores: dict[str, float] = defaultdict(float) # default value of 0.0 for any new key

    for rank, hit in enumerate(dense_hits):
        rrf_scores[hit["id"]] += 1.0 / (rank + _RRF_K)

    for rank, hit in enumerate(sparse_hits):
        rrf_scores[hit["id"]] += 1.0 / (rank + _RRF_K)

    # 4. Sort by RRF score descending, take top_k.
    #    Text lookup priority:
    #      1. ChromaDB's own document field (dense hits always carry it)
    #      2. id_to_text (covers BM25-only hits + is the canonical source)
    #    This handles orphaned ChromaDB docs (old syncs never deleted)
    #    that appear in dense results but aren't in the current seed.
    chroma_text: dict[str, str] = {hit["id"]: hit["document"] for hit in dense_hits}

    top_ids = sorted(rrf_scores, key=rrf_scores.__getitem__, reverse=True)[:top_k] # sorts by key by default, but we want to sort by value (the RRF score), so we use rrf_scores.__getitem__ as the key function, which retrieves the score for each id. reverse=True for descending order. Then we take the top_k ids.
    return [
        {
            "id":        id_,
            "text":      chroma_text.get(id_) or id_to_text.get(id_, ""),
            "rrf_score": round(rrf_scores[id_], 6),
        }
        for id_ in top_ids
    ]
