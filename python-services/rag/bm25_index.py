import re

import numpy as np
from rank_bm25 import BM25Plus


def _tokenize(text: str) -> list[str]:
    """
    Lowercase, strip punctuation (but keep underscores for C identifiers
    like ft_printf or NULL_ptr), discard single-char tokens.
    """
    cleaned = re.sub(r"[^a-z0-9_\s]", " ", text.lower())
    return [t for t in cleaned.split() if len(t) > 1]


class BM25Index:
    """
    In-memory BM25+ index over QA pair documents.

    Optionally stores a topic label per document, enabling topic-filtered
    search: after scoring all docs, results are filtered to the requested
    topic before returning. Post-filter is correct because BM25 has no
    concept of metadata — we score everything, then restrict the result list.

    Build once at startup, search many times at query time.
    """

    def __init__(self) -> None:
        self._bm25: BM25Plus | None = None
        self._ids: list[str] = []
        self._topics: list[str] = []   # parallel to _ids; "" if no topics stored

    def build(
        self,
        documents: list[str],
        ids: list[str],
        topics: list[str] | None = None,
    ) -> None:
        """
        Tokenize documents and build the BM25+ index.

        Args:
            documents: formatted QA texts (output of format_doc).
            ids:       stable doc IDs (output of make_doc_id), same order.
            topics:    optional topic label per doc, same order. If None,
                       topic filtering will not work but search still works.
        """
        if not documents:
            raise ValueError("Cannot build BM25 index from an empty document list")
        tokenized: list[list[str]] = [_tokenize(doc) for doc in documents]
        self._bm25 = BM25Plus(tokenized)
        self._ids = list(ids)
        self._topics = list(topics) if topics else [""] * len(ids)

    def search(
        self,
        query: str,
        n: int = 20,
        topic_filter: str | None = None,
    ) -> list[dict]:
        """
        Return up to n docs ranked by BM25+ score for query.

        Args:
            query:        raw user question string.
            n:            max number of results to return.
            topic_filter: if given, only return docs with this topic.
                          If None, return docs from all topics.

        Returns [] if index not built or query has no vocabulary overlap.

        Note — why no `score <= 0` early exit:
            BM25+ adds a delta floor to every document, so scores are always
            positive when any query token is in the vocabulary. A score<=0 break
            would be unreachable for any in-vocabulary query. Instead we guard
            upfront: empty tokenization and zero vocabulary overlap both return []
            before scoring runs, which is the only case scores would be zero.
        """
        if self._bm25 is None:
            return []

        tokens: list[str] = _tokenize(query)
        if not tokens:
            return []

        # Return [] when no query token exists in the index vocabulary.
        # BM25+ gives a positive floor score to every doc even with zero term
        # overlap — returning those results would be semantically meaningless.
        # idf=dict[str, float] idf score(inverse doc frequency) 
        # a mapping from every token seen during build() to its IDF score
        # Keys are the vocabulary terms; values are the precomputed IDF weights.
        if not any(t in self._bm25.idf for t in tokens):
            return []

        scores: np.ndarray = self._bm25.get_scores(tokens)
        ranked: list[tuple[int, float]] = sorted(enumerate(scores), key=lambda x: x[1], reverse=True) # enum() wrap each el with its index (0, 0.2), (1, 0.9),, lambda: sorts by score(second)

        results: list[dict] = []
        for idx, score in ranked:
            if topic_filter and self._topics[idx] != topic_filter:
                continue
            results.append({"id": self._ids[idx], "score": float(score)})
            if len(results) >= n:
                break

        return results
