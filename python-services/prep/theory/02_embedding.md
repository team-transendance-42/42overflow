RAG AI search system — cosine similarity is the core engine that makes it work.
============================

A vector is just a list of numbers that describe a point in space.

[3.0, 4.0]        ← 2D: like a point on a map (x=3, y=4)
[1.0, 2.0, 3.0]   ← 3D: like a point in a room (x, y, z)
[0.9, 0.1, 0.05]  ← still just numbers, but could mean anything

words and sentences get turned into vectors (called embeddings). The idea: words with similar meaning get similar numbers.
=============================

Magnitude = the length of the vector. Think of it as the straight-line distance from the origin (0,0) to your point.
=============================
Pythagoras: for right angle triangles, the square of the hypotenuse (diagonal) equals the sum of the squares of the other two sides.


|\
|  \
|    \   ← this diagonal is what we want(hypotenuse)
|      \
+--------
The rule:

diagonal² = side_a² + side_b²
diagonal  = sqrt( side_a² + side_b² )
===========================================

Magnitude = the straight-line distance from zero to your point.
