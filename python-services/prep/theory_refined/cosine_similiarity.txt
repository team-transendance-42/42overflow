Dense = vector where most positions contain a value.
Example: [0.12, -0.45, 0.88, ...]
Embeddings from LLMs are dense vectors.
NumPy = Python library for numerical arrays and vector operations.

Cosine (cosine similarity) = measure of how similar two vectors are.
similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

Query: "How to reset password?"
Embed query → dense vector.
Embed all documents → dense vectors.
Compute cosine similarity between query vector and document vectors.
Return documents with highest similarity.

"Dense + NumPy + cosine" usually means: store embeddings as dense vectors and use NumPy to calculate cosine similarity between them.
============================
I love cats

Tokens:

I      -> [1, 2, 3]
love   -> [4, 5, 6]
cats   -> [7, 8, 9]

A very old/simple approach would average them:

([1,2,3] + [4,5,6] + [7,8,9]) / 3
=
[4,5,6]

But modern embedding models don't do that.

What actually happens

The tokens go through a Transformer.

I      -> [1,2,3]
love   -> [4,5,6]
cats   -> [7,8,9]
         ↓
     Transformer
         ↓

Now each token changes based on the others:

I      -> [2,1,4]
love   -> [8,9,7]
cats   -> [6,7,8]

because "love" affects "cats", "cats" affects "love", etc. This is attention.

Then how do we get one vector?

Common methods:

CLS token
[CLS] I love cats

The model outputs a vector for [CLS].

That vector becomes the sentence embedding.

Pooling

Take all final token vectors and average them:

average(
 [2,1,4],
 [8,9,7],
 [6,7,8]
)

Many embedding models use mean pooling.

Why does sentence length not matter?

Whether you have:

cats

or

I really love small orange cats sleeping on sofas

the model finally compresses everything into:

[0.12, -0.55, ..., 0.88]

768 numbers.

The vector dimension stays fixed; only the values change.

Think of it like:

3 words    -> 768 numbers
300 words  -> 768 numbers

The Transformer's job is to squeeze the meaning of the whole text into that fixed-size vector.