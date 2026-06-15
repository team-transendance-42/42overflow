embeddings and local RAG

If later you want:

ask questions over your own docs
local search over notes / PDFs / code
“chat with my files”

then you need embeddings + retrieval.

Ollama has embedding support and recommends models such as embeddinggemma, qwen3-embedding, and all-minilm on its embeddings docs.

curl http://localhost:11434/api/embed -d '{
  "model": "embeddinggemma",
  "input": "What is epoll?"
}'
=============================
Very simple local RAG flow:

split your documents into chunks
make embeddings for each chunk
store vectors in a vector DB or even a simple local store
embed the user question
retrieve nearest chunks
send those chunks plus the question to the chat model

That feels like “the model learned my data,” but really it is retrieval, not weight training.



