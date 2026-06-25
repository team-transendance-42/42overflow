OOV = Out Of Vocabulary

"Vocabulary" just means the list of all words BM25 has ever seen in your documents.

Imagine BM25 is a librarian who read every book in the library and made a giant word list:

words I know: malloc, pointer, git, commit, segfault, norm, piscine, fork, memory, thread ...

In vocabulary = word is on the list
Out of vocabulary (OOV) = word is NOT on the list

  ---
he full picture in 3 steps

  User types:  "xyzzy blorp"he synonym problem you asked about (ptr vs pointer) is a different layer — BM25 can't help there. That's what
  the embedding search handles. BM25 only deals with exact words. If it knows the word → it searches. If it knows
  zero words from the question → return nothing immediately.
               ↓
  Step 1: tokenize → ["xyzzy", "blorp"]
               ↓
  Step 2: are ANY of these in our word list? → NO
               ↓
  Step 3: return []  ← stop, don't waste time scoring 200 docs

  vs. normal case:

  User types:  "what is malloc"
               ↓
  Step 1: tokenize → ["what", "is", "malloc"]
               ↓
  Step 2: is "malloc" in our word list? → YES
               ↓
  Step 3: score all docs, return top 20
===============
he synonym problem (ptr vs pointer) is a different layer — BM25 can't help there. That's what  the embedding search handles. BM25 only deals with exact words. If it knows the word → it searches. If it knows
  zero words from the question → return nothing immediately.
========================
  - Hybrid retrieval: dense (NumpyIndex cosine similarity) + sparse (BM25+) merged with Reciprocal Rank Fusion 
  (RRF)
  - Topic-aware: centroid detection narrows search to the right project before searching
  - Intro doc pinning: vague queries always get the overview doc first
  - Prompt grounding: strict rules prevent Gemma from hallucinating outside the context
  - Caching: repeated questions skip Ollama entirely
