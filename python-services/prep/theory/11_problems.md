
  ChromaDB stores QA pairs as vectors (numbers representing meaning).
  When you ask a question, your question gets turned into a vector too,
  and ChromaDB finds the QA pairs whose vectors are geometrically
  closest — "semantic" matching. "how do I free memory?" finds docs
  about free() and malloc() even if neither word appears in your
  question.

  BM25 (in Python RAM currently) is keyword matching with scoring. It
  finds QA pairs that share actual words with your question. Fast,
  in-memory, no model needed.

  fastembed (Python library) is what converts text → vectors. Every
  query, it runs a 768-dimension transformer model on CPU. This is the
  slow part — ~300ms every single time.

  Python RAG service currently does all three: loads QA pairs from
  seed.json + DB, runs fastembed, syncs to ChromaDB, builds BM25 index,
  and answers /rag/retrieve calls at query time.

  Go llm-server calls Python's /rag/retrieve on every community
  question, gets back 5 context snippets, builds a prompt, then streams
  Ollama.