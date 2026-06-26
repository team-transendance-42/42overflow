Ollama
======================================
messages:   	{role, content}
system prompt: 	role:system
role name:     "assistant"
extra fields: stream

=====================================
Gemini
=====================================
messages:     	{role, parts:[{text}]}
system prompt:  system_instruction, top-level field
role name:      "model"
extra fields:   system_instruction, multimodal parts
