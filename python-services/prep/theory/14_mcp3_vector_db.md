 What is "MCP to a Vector Database"?

  It means: you build an MCP server that wraps a vector database,
  exposing it as tools the LLM can call. Instead of hardcoding what
  context to retrieve, the LLM decides when to search and with what
  query.

  Pipeline comparison

  Your current pipeline (fixed, deterministic):
  User question
    → Go API
    → Python RAG service (FastAPI)
    → NumpyIndex.search() [0.05ms, in-process]
    → BM25Index.search() [in-process]
    → RRF merge
    → LLM generates answer
    → Response

  MCP + Vector DB pipeline (LLM-driven, agentic):
  User question
    → LLM (Claude/Ollama with MCP client)
    → LLM decides: "I need context" → calls semantic_search("pointer
  arithmetic")
    → MCP server → Vector DB (Qdrant/pgvector/ChromaDB)
    → Returns top-k docs to LLM
    → LLM decides: "not enough, let me also search for 'segfault'"
    → calls semantic_search again, or calls get_similar_questions
    → LLM now has full context → generates answer

  The key difference: in your current setup the retrieval logic is fixed
   code. In the MCP approach, the LLM reasons about retrieval itself.
   ================================
   
  SDK = Software Development Kit — a library that abstracts a protocol
  or API so you don't write raw HTTP/JSON manually.

  ┌─────────────────────────────┬───────────────────────────────────┐
  │             SDK             │           What it does            │
  ├─────────────────────────────┼───────────────────────────────────┤
  │ mcp Python SDK              │ Lets you write MCP servers in     │
  │                             │ Python with decorators            │
  ├─────────────────────────────┼───────────────────────────────────┤
  │ @modelcontextprotocol/sdk   │ Same but TypeScript               │
  │ (TS)                        │                                   │
  ├─────────────────────────────┼───────────────────────────────────┤
  │ anthropic Python SDK        │ Lets your code call Claude via    │
  │                             │ API                               │
  ├─────────────────────────────┼───────────────────────────────────┤
  │ chromadb                    │ The client SDK for ChromaDB       │
  │                             │ you're already using              │
  └─────────────────────────────┴───────────────────────────────────┘

  Without an SDK you'd write raw JSON-RPC messages over stdio by hand.
  The SDK gives you @server.list_tools(), @server.call_tool() decorators
   and handles the protocol. Your store.py already uses the chromadb SDK
   — same idea.
