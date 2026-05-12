---
  The one trick that matters most for a 4b model

  Keep top_k low (2-3) and chunks small (~100 tokens). A 4b model with 3
   precise chunks answers better than with 10 noisy ones. Your Python
  service currently defaults top_k=3 — that's right. Tune chunk size
  down if answers feel unfocused.

  The retrieval precision of Q&A + small atomic chunks with a low top_k
  is the fastest path to a smart-feeling RAG on a small local model.