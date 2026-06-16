NumPy is a Python library for fast numerical computing.
NumPy provides:

arrays
matrix multiplication
dot products
norms
cosine similarity

all optimized in C, so Python code stays short while execution is fast.
=================================

Instead of:

a = [1, 2, 3]
b = [4, 5, 6]

c = []
for i in range(len(a)):
    c.append(a[i] + b[i])

you do:

import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

c = a + b
============
A Python list stores references to Python objects:

list
 ├─ pointer -> Python int(1)
 ├─ pointer -> Python int(2)
 └─ pointer -> Python int(3)

Lots of memory overhead.

A NumPy array stores raw numbers continuously:

memory:
1 2 3 4 5 6

like a C array.

Why is it fast?

Most operations are implemented in C (and often use SIMD/vectorized CPU instructions).
===========================
When you do:

c = a + b

Python does not loop.

Instead it calls optimized C code:

for (i = 0; i < n; i++)
    c[i] = a[i] + b[i];

which runs much faster.
======================================
In embeddings

Suppose:

query = np.array([...768 numbers...])
doc   = np.array([...768 numbers...])

Cosine similarity:

np.dot(query, doc)

Under the hood:

sum = 0;
for (i = 0; i < 768; i++)
    sum += query[i] * doc[i];

Very fast because the data is contiguous in memory.
=========================================

