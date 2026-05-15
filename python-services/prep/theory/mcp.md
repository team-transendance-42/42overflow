MCP (Model Context Protocol) is an open standard introduced by Anthropic in November 2024 to standardize the way AI systems like LLMs integrate and share data with external tools, systems, and data sources. It provides a universal interface for reading files, executing functions, and handling contextual prompts. Wikipedia
The best mental model: think of it as USB-C for AI — one universal connector that eliminates the need for bespoke integrations between every model and every API. Essamamdani
Before MCP, if you wanted Claude to query your database, read a file, and call a REST API, you'd write three totally different custom integrations. And if you later switched to GPT or Gemini, you'd rewrite all three. MCP solves this by defining a protocol layer rather than an API layer — any host that speaks MCP can connect to any MCP server, regardless of whether the underlying model is Claude, GPT, Gemini, or a local Llama. Essamamdani
=============================
The three-layer architecture
Host — the application that embeds the LLM (Claude Desktop, your custom app, a VS Code extension). It contains both the model and an MCP client.
MCP Client — a protocol layer inside the host that manages connections to one or more MCP servers. It handles the handshake, capability negotiation, and message routing.
MCP Server — a lightweight, standalone process you write that exposes capabilities (tools, resources, prompts) to the client. It knows nothing about the LLM; it just speaks JSON-RPC.
==============================

