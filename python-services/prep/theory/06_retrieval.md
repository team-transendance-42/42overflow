
  now we have two indexes:
  - ChromaDB (dense): 55 QA pairs as 768-dim vectors, searched by cosine
   similarity
  - BM25 (sparse): 55 QA pairs tokenized, searched by keyword frequency
  =================  
  retriever.py has one job: given a question, ask both indexes for their
   top-20 results, then merge those two ranked lists into one using
  Reciprocal Rank Fusion.
  ========================  
  Why RRF( Reciprocal Rank Fusion) and not score averaging?
  ========================
  Dense scores are cosine similarities (roughly 0-1). BM25Plus scores
  are raw floats (can be 0.5 or 40.0 depending on corpus size and term
  frequency). They live in completely different numeric ranges —
  averaging them is meaningless.
  --------
   RRF sidesteps this entirely by throwing away the scores and using only
   rank position:

  rrf_score(doc) = Σ  1 / (rank_in_list + k)    k = 60

  With k=60, a doc ranked #1 in both lists scores 1/61 + 1/61 ≈ 0.033. A
   doc ranked #1 in only one list scores 1/61 ≈ 0.016. The k constant
  prevents rank-1 from dominating — a doc ranked #3 in both lists can
  beat a doc ranked #1 in one list and absent from the other.
  =================================
  Design decision: retriever.py is stateless

  hybrid_search() takes everything it needs as parameters — the BM25
  index and an id_to_text lookup dict. No import from main.py, no global
   state. This makes it testable in isolation and reusable.

  The caller (router.py) builds the lookup from qa_cache and
  passes it in.
  ===============================





















  