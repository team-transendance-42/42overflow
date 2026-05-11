1. PYTHAGORAS’ THEOREM (for right triangles)
If you have a right triangle (one angle is 90°), and the sides are a, b, and c (where c is the longest side, called the hypotenuse):

    a^2 + b^2 = c^2

Example: If a = 3 and b = 4, then c = sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5.

---

2. SINE AND COSINE (triangle helpers)
Sine of an angle (sin) = opposite side / hypotenuse
Cosine of an angle (cos) = adjacent side / hypotenuse

If you have a triangle with angle theta:
sin(theta) = opposite / hypotenuse
cos(theta) = adjacent / hypotenuse

---

3. COSINE SIMILARITY (comparing directions)
Imagine two arrows (vectors) from the same starting point. The cosine of the angle between them tells you how similar their directions are:
If they point the same way, cos(theta) = 1 (very similar)
If they are at 90 degrees, cos(theta) = 0 (not similar)
If they point opposite, cos(theta) = -1 (opposite)

===============================================
  The formula: cos(θ) = (A · B) / (|A| × |B|)
===============================================
  Think of A and B as two lists of numbers (vectors). For example:

  A = [1, 2, 3]
  B = [4, 5, 6]
  ---
  The Dot Product: A · B (the dot)

  The dot · means dot product — multiply matching pairs, then add them all up:

  A · B = (1×4) + (2×5) + (3×6)
        =   4  +  10   +  18
        = 32

  That's it. Pair up, multiply, sum.
  -------------------
  The Magnitude: |A| (the bars)

  The bars | | mean magnitude — the "length" of the vector.
  It's just Pythagoras in multiple dimensions:

  |A| = √(1² + 2² + 3²)
      = √(1 + 4 + 9)
      = √14
      ≈ 3.74

  Same for B:
  |B| = √(4² + 5² + 6²)
      = √(16 + 25 + 36)
      = √77
      ≈ 8.77

      = √14
      ≈ 3.74

  Same for B:
  |B| = √(4² + 5² + 6²)
      = √(16 + 25 + 36)
      = √77
      ≈ 8.77
---------------
  Putting it together
  cos(θ) = 32 / (3.74 × 8.77)
          = 32 / 32.8
          ≈ 0.97

---

4. HOW WE USE IT HERE
We turn text into vectors (lists of numbers). Cosine similarity tells us how similar two pieces of text are by comparing their vectors’ directions.

---

5. PRACTICE PROBLEMS

1. PYTHAGORAS:
   If a triangle has sides a = 6, b = 8, what is c?

2. SINE/COSINE:
   In a right triangle, the hypotenuse is 10, and one side is 6. What is cos(theta) for the angle next to the side of length 6?

3. COSINE SIMILARITY:
   If A = [1, 2] and B = [2, 4], what is cos(theta) between them?

Let me know if you want the answers or more practice!
