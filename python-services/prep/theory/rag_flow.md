Data flow

9 Student submits question (Community mode)
→ POST /api/community (Vite proxy → Go :8081)
→ Go RagAskStreaming handler
→ calls Python RAG /rag/ask (retrieves top-5 contexts + c
onfidence)
→ sends SSE meta event: { contexts, confidence }
→ acquires ollamaQueue slot (capacity-1 semaphore, same a
s Gemma)
→ builds strict prompt (question + retrieved contexts onl
y)
→ streams Gemma answer via existing StreamOllama infrastr
ucture
→ sends SSE token events (word by word)
→ sends SSE end event
→ Frontend parseSSEStream handles meta + token events
→ ragContexts and ragConfidence set from meta event
→ answer streams in word by word 
   -------------------- ## SSE Protocol
   
Community uses the same SSE wire format as Gemma/Gemini, with o
    ne extra event at the start:

```
event: meta
data: {"contexts":["post excerpt 1","post excerpt 2","post exce
    rpt 3"],"confidence":0.031}
    data: First
data:  word
data:  of
data:  answer
    ...
    event: end
    data:
    ```
   
The `meta` event fires immediately after retrieval (before Gemm
a starts generating). Contexts appear in the sources panel whil
e the answer streams in.