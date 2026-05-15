 How the Go RAG pipeline works — explained simply

  Think of it like a school library assistant helping a student find an
  answer:

  Browser (student asks)
      ↓  POST /api/community
  handlers/rag.go  — the librarian at the front desk
      ↓
  services/rag.go  — the research assistant (fetches books, builds the
  answer)
      ↓                              ↓
  Python RAG service             Ollama (Gemma)
  (finds relevant posts)         (writes the answer using those posts)
      ↓                              ↓
  Back to browser as SSE stream — word by word
  ===================