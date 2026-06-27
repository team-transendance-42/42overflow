FastEmbed is a Python library by Qdrant that runs embedding models locally using ONNX Runtime — no
  API call, no internet, no GPU required. ONNX is a format that lets ML models run on CPU efficiently.
  The model (nomic-embed-text-v1.5) converts text → a list of 768 floats (a vector). Similar texts
  produce similar vectors — that's the basis of semantic search.
