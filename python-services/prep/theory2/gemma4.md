gemma4:e4b is available on Ollama right now. The "E4B" stands for Effective 4B — it's a 26B Mixture of Experts model with only 4B active parameters, so it behaves like a 4B model in terms of compute and memory while having the capacity of a much larger one

  Good GPU (16 GB VRAM)
  → gemma4:26b — this is the sweet spot. MoE architecture means only
  3.8B parameters active per token, so it punches well above its weight
  on speed while delivering near-top-tier reasoning.

  Large GPU (20+ GB VRAM)
  → gemma4:31b — best Gemma exists for coding and reasoning, full stop
  =============
  
  Small GPU (4–8 GB VRAM)
  → gemma4:e4b (9.6 GB) can offload layers to GPU but is disappointing —
   MMLU-Pro only 69.4% despite the "gemma4" name. Honestly gemma3:4b
  still wins here for pure text.