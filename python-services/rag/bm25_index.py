import re

from rank_bm25 import BM25Plus # BM25Plus is a variant of BM25 that adds a delta to the score, ensuring that matching documents always score above non-matching ones. This is important for retrieval tasks, especially with small corpora where common terms can lead to negative IDF scores in BM25Okapi.


def _tokenize(text: str) -> list[str]:
    """
    Lowercase, strip punctuation (but keep underscores for C identifiers
    like ft_printf or NULL_ptr), discard single-char tokens.

    We keep underscores because `[^a-z0-9_\\s]` treats _ as a word char.
    Single-char tokens (remnants of 'q:' → 'q', 'a:' → 'a', '%d' → 'd')
    are filtered out — they add noise, not signal.
    """
    cleaned = re.sub(r"[^a-z0-9_\s]", " ", text.lower())
    return [t for t in cleaned.split() if len(t) > 1]


class BM25Index:
    """
    In-memory BM25+ index over a fixed document corpus.

    Uses BM25Plus instead of BM25Okapi to avoid negative IDF scores.
    BM25Okapi penalizes terms that appear in more than ~50% of documents
    with negative IDF, which our small corpus (40 QA pairs) hits easily
    for common words. BM25Plus adds a delta shift so matching docs always
    score above non-matching ones — correct behavior for retrieval.

    Build once at startup (from the same texts embedded into ChromaDB),
    then search many times — one search per incoming user question.
    """

    def __init__(self) -> None:
        self._bm25: BM25Plus | None = None
        self._ids: list[str] = []

    def build(self, documents: list[str], ids: list[str]) -> None:
        """
        Tokenize documents and build the BM25+ index.

        documents and ids must be the same length and in the same order.
        Raises ValueError if documents is empty — an empty index would
        silently return nothing on every query, masking a data problem.
        """
        if not documents:
            raise ValueError("Cannot build BM25 index from an empty document list")
        tokenized = [_tokenize(doc) for doc in documents]
        self._bm25 = BM25Plus(tokenized)
        self._ids = list(ids)

    def search(self, query: str, n: int = 20) -> list[dict]:
        """
        Return up to n docs ranked by BM25+ score for query.

        Returns [] if the index was never built (safe — the hybrid
        retriever will fall back to dense-only results).

        Only docs with score > 0 are returned. With BM25Plus, a score of
        exactly 0 means none of the query tokens appeared anywhere in the
        corpus vocabulary — true no-match. Docs with any vocabulary overlap
        always score > 0 due to the delta shift.
        """
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        top_n = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:n]
        return [{"id": self._ids[i], "score": float(s)} for i, s in top_n if s > 0]
