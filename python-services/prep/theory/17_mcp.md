MCP = Model Context Protocol

It is a standard that lets an AI connect to external tools in a consistent way.

Think of it as:

USB-C for AI tools
---
Just as USB-C lets you connect keyboards, monitors, and drives through one standard, MCP lets AI connect to databases, GitHub, filesystems, APIs, and apps through one standard.
----
Before MCP

Every tool needed custom code:

Claude → GitHub API (custom integration)

Claude → PostgreSQL (custom integration)

Claude → Slack API (custom integration)
---
With MCP

Everything exposes an MCP server:

Claude
   ↓
 MCP
   ↓
 ├── GitHub MCP Server
 ├── PostgreSQL MCP Server
 ├── Filesystem MCP Server
 ├── Slack MCP Server
 └── Weather MCP Server

Claude only needs to understand MCP.
----
Example: Filesystem MCP

User:

Find all TODO comments in my project.

Claude:

Calls filesystem tool:
list_files()

Then:

read_file("main.py")
read_file("utils.py")

Then answers.

Example: GitHub MCP

User:

Show open pull requests.

Claude calls:

github.list_pull_requests()

Returns:

[
  {"title":"Fix login"},
  {"title":"Add dark mode"}
]

Claude summarizes.
-------------
Example: PostgreSQL MCP

User:

How many customers registered this month?

Claude:

SELECT COUNT(*)
FROM customers
WHERE created_at >= '2026-06-01';

MCP executes it and returns result.
---
Common MCP Servers
Filesystem

Access files:

read_file()
write_file()
list_directory()
GitHub

Access repositories:

get_issue()
create_pr()
list_commits()
Git

Access local git repo:

git_status()
git_diff()
git_commit()
Database

Examples:

PostgreSQL
MySQL
SQLite

Tools:

execute_query()
list_tables()
---
Why is MCP important?

Without MCP:

Tool A -> custom code
Tool B -> custom code
Tool C -> custom code

With MCP:

Any AI
   ↓
 MCP
   ↓
 Any MCP tool

One protocol for everything.
====
Is MCP the same as function calling?

Not exactly.

Function calling

A model calls:

{
  "tool": "get_weather",
  "city": "Amsterdam"
}

This is the mechanism.
---
MCP

Defines:

how tools are discovered
how tools are described
how tools are called
how results are returned

So:

Function Calling = making the call

MCP = complete standard for tools
=================================
todo
=================================
Gemma 3
   ↓
 MCP Client
   ↓
 ├── Filesystem MCP
 ├── PostgreSQL MCP
 ├── Weather MCP
 └── GitHub MCP

Then your local Gemma can:

know today's date
check weather
search files
query databases
inspect Git repositories

even though the model itself is completely offline.

That's why modern AI assistants are becoming LLM + MCP tools, rather than just a standalone model.
===================================
An MCP server is a program that exposes tools to an AI through the Model Context Protocol (MCP).

Think of it as a translator between the AI and some resource.

Claude / ChatGPT / Gemma
          ↓
      MCP Client
          ↓
      MCP Server
          ↓
     Real Resource

Example:

Gemma
  ↓
Filesystem MCP Server
  ↓
Your files on disk

The AI doesn't directly read files. It asks the MCP server:

list_files()
read_file("main.c")

The MCP server performs the action and returns the result.
---
Example: Weather MCP Server
Gemma
  ↓
Weather MCP Server
  ↓
Weather API

User:

What's the weather in Amsterdam?

Gemma asks:

get_weather("Amsterdam")

The MCP server:

Calls the weather API.
Gets the forecast.
Returns structured data.

Gemma writes the answer.

Example: GitHub MCP Server
Gemma
  ↓
GitHub MCP Server
  ↓
GitHub

User:

Show open issues.

Gemma asks:

list_issues()

The MCP server talks to GitHub and returns the results.
---
MCP Client vs MCP Server
==============================
MCP Client
==============================

Lives inside the AI application.

Gemma
  ↓
MCP Client

Responsible for:

discovering tools
calling tools
receiving results
MCP Server

Lives outside the AI.

MCP Server
  ↓
Database

Responsible for:

providing tools
executing tools
returning results
==========================
MCP Server
==========================
Lives outside the AI.

MCP Server
  ↓
Database

Responsible for:

providing tools
executing tools
returning results


