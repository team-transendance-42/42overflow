Why one-doc-per-post fails with near-duplicates:
  The embedding model produces one vector for the concatenated blob. When 3 near-identical comments are
  joined, the vector is the centroid of all three — slightly polluted in all directions. The LLM then
  receives the full blob, sees fcntl(fd, F_SETFL, O_NONBLOCK) once and fcntl(fd, FSETFL, ONONBLOCK)
  twice, and picks inconsistently.

  Why per-comment fixes this:
  Each comment gets its own embedding vector — sharper, not averaged. The retriever ranks them
  independently. Mystery User's complete answer scores higher cosine similarity for most questions
  about that topic → it wins the top-k slot. The typo versions don't make it into the LLM's context.

  Why cap at N comments:
  Without a cap, a viral post with 200 comments produces 200 docs with the same post question text.
  BM25 sees 200 documents all containing the keyword "poll" and the topic score inflates artificially.
  A cap of 15 keeps the corpus bounded while covering any realistic 42school post.

  Why newest N (not oldest N):
  First answers are often incomplete. Later comments correct, add, or clarify. Recency biases toward
  evolved community knowledge.
  =======================
   Pros
  
  - Mystery User's answer naturally outranks typo versions via cosine similarity — no heuristic needed
  - Clean single-answer context per retrieved doc → LLM can reproduce it faithfully
  - Corpus grows by avg-comments-per-post factor (~2–5x for 42school data) — at this scale NumpyIndex
  handles it in <1ms
  - On next sync, evicted comments (beyond the 15 cap) disappear from ChromaDB automatically — no
  explicit delete logic needed since sync rebuilds from scratch
  
  Cons

  - Same post question text appears N times in BM25 index — keyword score for that topic slightly
  inflated (mitigated by RRF's rank-based weighting rather than raw score)
  - Doc IDs change → first deploy after this change: ChromaDB will see all-new IDs and re-embed
  everything (one-time cost, ~2min for current corpus size)
  - A post where only comment #16 is the definitive answer gets evicted if 15 newer low-quality
  comments exist — but this is rare and fixable later with likes-pinning

