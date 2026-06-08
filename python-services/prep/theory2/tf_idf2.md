 ---
  TF x IDF = TF-IDF score
  ---
  The setup (the corpus)

  Document 1: "The cat sat on the mat."
  Document 2: "The dog played in the park."
  Document 3: "Cats and dogs are great pets."

  We're asking: how important is the word "cat" to each document?

  ---
  Step 1 — TF (how often does "cat" appear in this doc?)

  Doc 1: "cat" appears 1 time out of 6 words → 1/6 = 0.167
  Doc 2: "cat" appears 0 times              → 0/6 = 0
  Doc 3: "cats" appears 1 time out of 6     → 1/6 = 0.167

  ---
  Step 2 — IDF (how rare is "cat" across ALL docs?)

  3 total docs. "cat" appears in 2 of them (Doc 1 and Doc 3).

  IDF = log(3/2) = log(1.5) ≈ 0.176

  The rarer a word is across documents, the higher this number. Common words like "the" would score near 0 here.

  ---
  Step 3 — Multiply them (the final score)
TF * IDF
  Doc 1: 0.167 x 0.176 = 0.029  ← "cat" matters here
  Doc 2: 0     x 0.176 = 0      ← "cat" not here at all
  Doc 3: 0.167 x 0.176 = 0.029  ← "cat" matters here equally

  ---
  TF-IDF = TF x IDF

  For Doc 1:

  TF  = 1/6 = 0.167   (cat appeared 1 time out of 6 words)
  IDF = 0.176          (cat is in 2 out of 3 docs, so moderately rare)

  TF-IDF = 0.167 x 0.176 = 0.029

  That's it. Nothing fancy — just two numbers multiplied together.

  Why multiply and not add?

  Because both conditions must be true to matter:

  - Word appears a lot in this doc (high TF) → probably relevant
  - Word is rare across all docs (high IDF) → probably meaningful

  If either is zero, the score is zero. Multiplying enforces that both matter. Adding would let a very high TF compensate for a zero IDF (e.g., the
  word "the" appears everywhere — useless as a signal).
  because it treats "cat" and "cats" as different words. This is exactly the keyword-matching limitation from before.