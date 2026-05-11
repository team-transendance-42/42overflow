A vector is just a list of numbers with a fixed length (its "dimension").
Every number is called a "component" or "dimension".

In geometry: a 2D vector [3, 4] is an arrow pointing to x=3, y=4.
In ML: a vector is a point in N-dimensional space.

The KEY idea: if two vectors point in the SAME direction, the texts they
represent share the same meaning. Direction = meaning.
In math / ML:
A vector has a fixed dimension — it's a coordinate in N-dimensional space. You can't add or remove dimensions, because that would change the space entirely.

2D vector:  [3.0,  4.0]               ← always exactly 2 numbers
3D vector:  [3.0,  4.0,  1.5]         ← always exactly 3 numbers
768D embedding: [0.12, -0.45, ...(768 total)] ← always exactly 768 numbers
The "fixed" constraint is what makes comparison meaningful. If nomic-embed-text sometimes returned 768 numbers and sometimes 300, cosine similarity would be impossible — the dot product sum(a_i * b_i) requires both vectors to have the same number of dimensions.
In Python it's just a plain list[float] — nothing enforces the length. The contract is:

every document you embed with nomic-embed-text → always 768 floats
every query you embed with nomic-embed-text → always 768 floats
therefore comparison is always valid
The closest C++ equivalent to a fixed-size ML vector is:


std::array<float, 768> embedding;   // fixed at compile time
or in practice, a raw float[768]. 
===================================================

 "direction" is the geometric core of how embeddings work. The actual values of the components don't matter as much as the overall direction they point in. Two vectors can have very different numbers but still point in the same direction, meaning their texts are semantically similar.
-------------------------------------------

In 2D — Direction is Literally an Arrow
A vector [3, 4] is an arrow from the origin (0,0) to the point (3,4):


y
^
4 |        * ← tip of [3, 4]
3 |       /
2 |      /   ← the arrow
1 |     /
0 +--3---> x
Now scale it: [6, 8] is the same direction, just twice as long:


y
^
8 |            * ← tip of [6, 8]
4 |        *   ← tip of [3, 4]
0 +--3--6---> x
Both arrows point at the same angle. That's what "same direction" means — same ratio between components, regardless of magnitude.

[3, 4] and [6, 8] and [0.3, 0.4] all point identically. Cosine similarity between all three = 1.0.
=============================================

Why Ratio = Meaning
When the embedding model trains, it learns to encode meaning as a direction in space. For example, in a toy 2D space:


          "animal" axis
               ^
               |
    cat [0.9, 0.1]  →  points mostly "animal-ward"
    dog [0.8, 0.2]  →  same rough direction
               |
               +-----------> "tech" axis
                        database [0.05, 0.95]  →  points mostly "tech-ward"
cat and dog point roughly the same direction → high cosine similarity.

cat and database point perpendicular directions → similarity ≈ 0.

The magnitude (how long the arrow is) is irrelevant — you could write "cat" once or write it a thousand times, the direction stays the same. That's why cosine divides by magnitude: it strips out length and keeps only direction.
==============================================
Cosine Measures the Angle Between Arrows
==============================================

cos(0°)   = 1.0   → same direction    → same meaning
cos(45°)  = 0.71  → somewhat similar
cos(90°)  = 0.0   → perpendicular     → unrelated
cos(180°) = -1.0  → opposite          → opposite meaning (rare in practice)

     cat [0.9, 0.1]
      \
       \  ← small angle → high cosine
        \
    dog [0.8, 0.2]


     cat [0.9, 0.1]
      |
      |  ← 90° angle → cosine = 0
      |
  database [0.05, 0.95] ──────>
  ===============================

  In 768 Dimensions — Same Idea, Unvisualizable
You can't draw 768D space, but the math is identical:

# 3D: direction = angle in 3D space
cat_3d = [0.9, 0.1, 0.05]
dog_3d = [0.8, 0.2, 0.10]

# 768D: direction = angle in 768D space
cat_768d = [0.031, -0.124, 0.887, 0.003, ...]   # 768 numbers
dog_768d  = [0.029, -0.118, 0.901, 0.001, ...]   # similar pattern
The formula (A·B) / (|A|x|B|) computes the same angle, just across 768 terms instead of 2 or 3. The geometry is the same — you just can't draw it.

