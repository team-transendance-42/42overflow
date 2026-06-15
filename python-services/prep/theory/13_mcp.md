
● MCP (Model Context Protocol) is an open standard that lets AI assistants connect to external tools, data sources, and
  services in a structured way.

  The problem it solves

  Without MCP, every AI integration is custom-built: "write a plugin for this editor," "write a connector for that
  database." MCP standardizes how AI models discover and call external capabilities.

  How it works

  Your AI (Claude)  <-->  MCP Client  <-->  MCP Server  <-->  External resource
                                           (e.g. filesystem,
                                            database, GitHub,
                                            Slack, etc.)

  1. MCP Server — a small process that exposes tools, resources, and prompts via a defined protocol. It sits in front of
   your database, filesystem, API, etc.
  2. MCP Client — the AI's side (e.g., Claude Code) that discovers available servers and calls them.
  3. Transport — communication happens over stdio (local process) or HTTP/SSE (remote server).

  What a server exposes

  ┌───────────┬───────────────────────────┬──────────────────────┐
  │  Concept  │        What it is         │       Example        │
  ├───────────┼───────────────────────────┼──────────────────────┤
  │ Tools     │ Functions the AI can call │ read_file, run_query │
                                            database, GitHub,
                                            Slack, etc.)

  1. MCP Server — a small process that exposes tools, resources, and prompts via a defined protocol. It sits in front of your database, filesystem,
  API, etc.
  2. MCP Client — the AI's side (e.g., Claude Code) that discovers available servers and calls them.
  3. Transport — communication happens over stdio (local process) or HTTP/SSE (remote server).
  resource
                                           (e.g. filesystem,
                                            database, GitHub,
                                            Slack, etc.)

  1. MCP Server — a small process that exposes tools, resources, and
  prompts via a defined protocol. It sits in front of your database,
  filesystem, API, etc.
  2. MCP Client — the AI's side (e.g., Claude Code) that discovers
  available servers and calls them.
  3. Transport — communication happens over stdio (local process) or
  HTTP/SSE (remote server).

  What a server exposes

  ┌───────────┬───────────────────────────┬──────────────────────┐
  │  Concept  │        What it is         │       Example        │
  ├───────────┼───────────────────────────┼──────────────────────┤
  │ Tools     │ Functions the AI can call │ read_file, run_query │
  ├───────────┼───────────────────────────┼──────────────────────┤
  │ Resources │ Data the AI can read      │ A file, a DB row     │
  ├───────────┼───────────────────────────┼──────────────────────┤
  │ Prompts   │ Reusable prompt templates │ "Summarize this PR"  │
  └───────────┴───────────────────────────┴──────────────────────┘

  Concrete example

  Claude Code connects to MCP servers defined in your config. When you
  ask "search my Gmail," Claude Code:
  1. Finds the Gmail MCP server
  2. Calls its search tool with parameters
  3. Gets results back as structured data
  4. Uses that in its response

  Why it matters

  - Composable — any server works with any MCP-compatible AI
  - Local or remote — can run on your machine or as a hosted service
  - Secure — you control what servers are connected and what permissions
   they have

  In your project you already have Gmail, Google Calendar, and Google
  Drive MCP servers configured (visible in the deferred tools list).