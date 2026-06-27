
To run an LLM locally, you need:

* an inference engine: Ollama / llama.cpp / LM Studio
* a model file: usually a quantized model
* enough RAM or VRAM
* a way to call it: CLI, REST API, Python, Go, etc.

Quantization reduces memory use and compute cost by storing weights in lower precision, such as 8-bit or 4-bit. Hugging Face documents 8-bit and 4-bit quantization support, and llama.cpp supports multiple quantization levels including 4-bit and 8-bit style formats for local inference.

So the stack is:

your app -> local server -> local model -> response
=======================================

Ollama

fastest path
minimal setup
simple API from Go, Python, JS
easy model pull/run/remove/list

Ollama’s docs show:

install on Linux with curl -fsSL https://ollama.com/install.sh | sh
start with ollama serve
run models with commands like ollama run gemma4
pull models with ollama pull ...
list with ollama ls
=================
hardware reality
=================

CPU only: Works, but slower.

Good for:
1B to 4B models
sometimes 7B quantized models if you are patient

GPU: Much better.

Ollama’s Linux docs explicitly mention optional CUDA setup for NVIDIA and ROCm for AMD, and recommend checking NVIDIA with nvidia-smi.
---
Model size rule of thumb

Bigger model = more memory + slower.
Quantized models help a lot.

Practical beginner sizes:

1B–4B: easiest
7B–8B: sweet spot for many laptops/desktops
14B+: often needs stronger hardware
==============================

Good beginner strategy:

one small instruct model
one coding model
one embedding model

Example categories:

general chat: Gemma / Qwen / Llama family
coding: code-focused instruct variants
embeddings: embedding-specific model

I am avoiding naming a “single best current model” beyond families because that changes fast and depends heavily on your hardware.
=============================

“It is slow”
use a smaller model
use quantized models
use GPU if available
keep model loaded with keep_alive

“Server not reachable”

Make sure ollama serve is running, or that systemd service is started.

“NVIDIA not used”

Check:

nvidia-smi

Ollama Linux docs explicitly point to that for CUDA verification.

“Need logs”
journalctl -e -u ollama

Documented in Ollama Linux docs.
======================

