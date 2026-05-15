import re

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
        self._bm25:   BM25Plus | None = None
        self._ids:    list[str]       = []
        self._topics: list[str]       = []   # parallel to _ids; "" if no topics stored

    def build(
        self,
        documents: list[str],
        ids:       list[str],
        topics:    list[str] | None = None,
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
        tokenized    = [_tokenize(doc) for doc in documents]
        self._bm25   = BM25Plus(tokenized)
        self._ids    = list(ids)
        self._topics = list(topics) if topics else [""] * len(ids)

    def search(
        self,
        query:        str,
        n:            int = 20,
        topic_filter: str | None = None,
    ) -> list[dict]:
        """
        Return up to n docs ranked by BM25+ score for query.

        Args:
            query:        raw user question string.
            n:            max number of results to return.
            topic_filter: if given, only return docs with this topic.
                          If None, return docs from all topics.

        Returns [] if index not built or no tokens match.
        """
        if self._bm25 is None:
            return []

        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked:
            if score <= 0:
                break
            if topic_filter and self._topics[idx] != topic_filter:
                continue
            results.append({"id": self._ids[idx], "score": float(score)})
            if len(results) >= n:
                break

        return results
