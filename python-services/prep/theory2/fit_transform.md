Classic ML pattern — fit learns from the whole corpus, transform applies what was learned to a single input.
==============================================================
fit(corpus)                          transform(text)
==============================================================
input:  all docs                     input:  one doc
output: stores idf weights           output: returns tfidf vector
runs:   ONCE                         runs:   for every query/chunk
What each does conceptually:
corpus = ["dog bites man", "man bites dog", "dog runs fast"]

fit() builds: 3 docs total, + 1 not to have negatve idf for words that appear in all docs
  df["dog"] = 3  → idf = log(3/4) + 1
  df["man"] = 2  → idf = log(3/3) + 1
  df["bites"] = 2 → idf = log(3/3) + 1
  df["runs"] = 1  → idf = log(3/2) + 1  ← rare = higher idf
  df["fast"] = 1  → idf = log(3/2) + 1

transform("dog runs") uses those stored idfs: total 2 tokens, so tf = 0.5 for each, then multiplied by idf:
  tf["dog"]  = 0.5 * idf["dog"]   ← common word, penalized
  tf["runs"] = 0.5 * idf["runs"]  ← rare word, rewarded
  --------------------------------
Why both in RAG specifically:
RAG pipeline:

  [all chunks] → fit() → stored idf weights
                                ↓
  [user query] → transform() → query vector
  [each chunk] → transform() → chunk vector  ← same idf scale!
                                ↓
                         cosine similarity → top-k chunks → LLM
---------------------------
Same pattern exists in sklearn (TfidfVectorizer.fit() / .transform()), and it's why you never fit on test data — the learned statistics must come only from the corpus you're indexing.
------------------------------
text = "dog runs"
corpus vocab = ["bites", "dog", "fast", "man", "runs"]  (size 5)

Dense vector (array):   [0.0,  0.42, 0.0,  0.0,  0.61]
                         bites  dog   fast   man   runs

Sparse vector (dict, aka map(key, val)):   {"dog": 0.42, "runs": 0.61}
                         ← only non-zero terms stored