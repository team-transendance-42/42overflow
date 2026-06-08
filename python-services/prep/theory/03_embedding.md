During training, the model was shown billions of sentence pairs labeled as semantically similar or different:

("cat", "feline") → positive pair → pushed together in 768D space
("cat", "database") → negative pair → pushed apart

After training, "cat" and "feline" end up as 768-dimensional vectors that point in nearly the same direction — even though they share zero characters. Cosine similarity between them is ~0.97.

The key insight: BoW asks "do these sentences share the same tokens?" — Embeddings ask "do these sentences point in the same direction in meaning-space?"
===============================================================================
How Embeddings Work — Under the Hood
===============================================================================
Step 0: The Big Idea
Imagine you have a magic room with 768 dials. Each word or sentence gets its own unique combination of dial settings. Words that mean similar things end up with similar dial combinations. That's it. An embedding is just a list of 768 numbers — the dial settings for that piece of text.
------------------------------------------------------------------
Step 1: Turning Words into Numbers (Tokenization)
------------------------------------------------------------------
The computer can't read letters. It only knows numbers. So first, every word gets chopped into tokens and each token gets a number ID from a fixed dictionary (~30,000 entries):
"The cat sat" → ["The", "cat", "sat"] → [1996, 4937, 2938]
The dictionary is fixed, so "cat" always maps to 4937. This is the first step in turning text into a vector.

Rare words get split up:
"feline" → ["fe", "##line"] → [7959, 8126]
The ## means "this piece continues the previous word." 
The actual reason "feline" ≈ "cat" in embedding space:
It's the distributional hypothesis: words that appear in similar contexts have similar meanings. During training, the model saw billions of sentences like:
"feed your cat / feline twice a day"
"the cat / feline sat on the mat"
"my cat / feline is very fluffy"
Because "cat" and "feline" kept appearing in the same kinds of sentences, with the same surrounding words, their vectors got pushed together through contrastive learning. That's it.
The model learned similarity from context patterns across billions of sentences — not from shared letters or subword tokens.
------------------------------------------------------------------
Step 2: Token Lookup Table (The First Layer)
------------------------------------------------------------------
Now each token ID looks up its own row in a giant table. The table has ~30,000 rows x 768 columns. Each row is already a vector — the starting "personality" of that token, learned during training.
token 4937 ("cat") → [ 0.12, -0.45, 0.89, 0.03, ... ]  ← 768 numbers
token 7959 ("fe")  → [ 0.31,  0.11, 0.22, 0.77, ... ]  ← 768 numbers
At this point the vectors are dumb — "cat" near a river and "cat" the animal have identical vectors. Context hasn't been applied yet.
------------------------------------------------------------------
tep 3: Attention — Where the Magic Happens
------------------------------------------------------------------
This is the Transformer. It runs 12 layers, each asking every token: "hey, which other tokens in this sentence should I be paying attention to?"

Think of it like a classroom. Each student (token) writes a little note to every other student saying "how much do I care about you right now?" — and updates their own understanding based on the replies.

Sentence: "I went to the bank to fish"
          ↑                      ↑
       "bank" looks at "fish"  → probably a river bank
       
Sentence: "I went to the bank to deposit money"
       "bank" looks at "deposit" → probably a financial bank
-----

After attention, the vector for the word "bank" is different in each sentence. Same word, different meaning → different vector. That's context-awareness.

Each of the 12 layers refines this further. Early layers catch grammar ("is this a noun?"). Later layers catch meaning ("is this about money or nature?").
------------------------------------------------------------------
Step 4: Pooling — Collapse to One Vector
------------------------------------------------------------------
After the 12 layers you have one 768-number vector per token. But you need one vector for the whole sentence.

The simplest method: mean pooling — just average all the token vectors together, dimension by dimension.
"cat sat"  after attention:
  "cat" → [0.9, 0.1, 0.05]
  "sat" → [0.3, 0.7, 0.20]
  average → [0.6, 0.4, 0.125]  ← the sentence vector

Now the whole sentence is one point in 768D space.
------------------------------------------------------------------
Step 5: How Training Taught It Meaning
The model didn't just randomly assign positions. It was trained on billions of sentence pairs with a simple rule:

"cat" and "feline" are similar → push their vectors closer together
"cat" and "database" are different → push their vectors further apart
This is called contrastive learning. Do this billions of times across all of human language on the internet, and the 768D space starts to organize itself like a map

   animal corner:   cat, dog, kitten, feline, puppy...
   tech corner:     database, SQL, server, query...
   emotion corner:  happy, joy, excited, love...

   Sentences that mean the same thing — no matter which exact words are used — end up landing in the same neighborhood on this map.
--------------------------------------------------------------------
Step 6: Cosine Similarity — Reading the Map
Two vectors pointing in the same direction on the map = same meaning.

angle = 0°   → similarity = 1.0  (identical meaning)
angle = 90°  → similarity = 0.0  (unrelated)
angle = 180° → similarity = -1.0 (opposite meaning)

"The cat sat" and "The feline rested" land almost in the same spot → angle ~5° → similarity ~0.99.

"The cat sat" and "deploy the database" land far apart → angle ~85° → similarity ~0.08.

This is exactly what your cosine_similarity() function computes — the angle between two 768-number arrows.
---------------------------------------------------------------------
pipeline:
"the cat sat"
      ↓
  Tokenizer          → [1996, 4937, 2938]
      ↓
  Lookup table       → 3 x [768 numbers]
      ↓
  12 attention layers → tokens understand each other
      ↓
  Mean pooling        → 1 x [768 numbers]
      ↓
  [0.12, -0.45, 0.89, ...]   ← embedding
----------------------------------------------------------------------

 Every model ships its own tokenizer, trained separately. They differ in algorithm, vocabulary size, and what they were optimized for:
 Model              Algorithm          Vocab size
-------------------------------------------------
BERT (Google)      WordPiece          ~30,000
GPT-4 (OpenAI)     BPE (tiktoken)     ~100,000
Claude (Anthropic) BPE variant        ~100,000+
LLaMA (Meta)       SentencePiece BPE  ~32,000
