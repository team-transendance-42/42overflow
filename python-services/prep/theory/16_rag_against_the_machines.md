A function call in machine learning / AI means:
the model is told to use an external tool (a function/code/API) to get an answer instead of only generating text.

Example:

User: “What’s the weather in Amsterdam?”
Model → calls function: get_weather("Amsterdam")
System returns data → model formats answer

So it’s not “learning”, it’s using tools.
--------------

1) What is a function call (AI/ML context)

A function call = structured request to run code

It usually includes:

function name (e.g. search_web)
inputs (arguments)
output comes from external system

The model does NOT execute it itself.

2) Why it exists

LLMs alone cannot:

access live data (weather, stocks)
do reliable calculations
query databases
interact with apps

Function calling fixes this by connecting AI → tools.
--------------------
1) What is a function call (AI/ML context)

A function call = structured request to run code

It usually includes:

function name (e.g. search_web)
inputs (arguments)
output comes from external system

The model does NOT execute it itself.
----------------------
2) Why it exists

LLMs alone cannot:

access live data (weather, stocks)
do reliable calculations
query databases
interact with apps

Function calling fixes this by connecting AI → tools.
--------------------
2. Machine Learning (ML)

System learns patterns from data.

Types:

Supervised learning → labeled data (cats vs dogs)
Unsupervised learning → clustering (no labels)
Reinforcement learning → learns via rewards

👉 Output = prediction (not tool use)
-----------------------
3. Deep Learning (DL)

Subset of ML:

uses neural networks
works on images, speech, text
e.g. GPT, CNNs
----------------------
4. Large Language Models (LLMs)

(e.g. GPT models)

trained on huge text data
predict next word
can answer, summarize, code

BUT:

no real-time knowledge
no direct actions unless tools added
----------------------
5. AI with Function Calling (Tool-using AI)

This is modern LLM + tools:

LLM +:

APIs
databases
calculators
web search
code execution
This is what ChatGPT uses when it “calls tools”
---------------------
4) Key difference: ML vs Function calling
Machine Learning:
learns patterns
produces predictions
no external actions

Example:

predict house price = €320k

Function calling:
does NOT “predict”
decides to ask another system
gets real result

Example:

call get_house_price() → returns real listing data
-----------------------
5) Simple analogy
Machine learning = brain that guesses
Function calling = brain that uses tools

Like:

ML = student who knows answers
Function calling = student who checks calculator / internet
--------------------------
6) In modern AI systems (important)

Today’s AI often combines:

LLM (thinking + language)
ML models (vision, ranking)
Function calls (tools)
Agents (multi-step tool use)

This is called: tool-augmented AI / agentic AI
---------------
jemma3 and free gemini api have curr date in 2024:
Solution 1: Inject the current date in the prompt

Before every user message:

from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""
Today is {today}.
Answer using this date when needed.
"""

Now Gemma knows the current date.

Solution 2: Function calling / tools

Create a tool:

from datetime import datetime

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")
---------------------------
Typical local LLM architecture
User
  ↓
Gemma 3
  ↓
Tool Router
  ├── Date Tool
  ├── Weather API
  ├── Web Search
  ├── Calculator
  └── Database
  ↓
Gemma
  ↓
Answer

This is how modern assistants work. The LLM does the language; tools provide live data
---------------------------
At a high level, ChatGPT, Claude, and Claude Code are built from the same core idea:

User
 ↓
LLM
 ↓
Tools
 ↓
LLM
 ↓
Answer

The differences are in the model, tools, and workflow.
---------------------------
User
 ↓
GPT-5.5
 ↓
Tool selection
 ├── Web Search
 ├── Python
 ├── File Analysis
 ├── Image Generation
 ├── Memory
 └── Other tools
 ↓
GPT-5.5
 ↓
Answer
---
Features:

General-purpose assistant
Web access
Image generation
Data analysis
Memory
Tool calling
==============================
User
 ↓
Claude model
 ↓
Tool selection
 ├── Web Search
 ├── MCP Tools
 ├── Databases
 └── APIs
 ↓
Claude
 ↓
Answer

Very similar architecture.

Main differences:

Different model training
Different safety rules
Different reasoning style
Different context window
==============================
claude code

User
 ↓
Claude
 ↓
Terminal Commands
 ├── ls
 ├── grep
 ├── git
 ├── pytest
 ├── npm
 └── compiler
 ↓
Claude
 ↓
Answer

It can:

read files
edit files
run tests
execute shell commands
commit to Git
=================================
diff:
ChatGPT

Strong at:

general knowledge
research
multimodal tasks
images
broad assistance
Claude

Strong at:

long documents
code understanding
large context windows
Claude Code

Strong at:

actually working inside a codebase
modifying hundreds of files
running builds/tests
===============================
Are they machine learning?

Yes.

Under the hood:

Training Data
 ↓
Transformer Neural Network
 ↓
Trillions of parameters
 ↓
Next-token prediction

GPT, Claude, Gemma, Llama, Mistral are all:

Transformer models
Deep learning models
Large Language Models (LLMs)

The architecture is fundamentally very similar.
===========================













