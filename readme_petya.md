learning material:
---

  Languages:
   Go           https://go.dev/doc/                  
   Python 3.12  https://docs.python.org/3.12/        
   TypeScript   https://www.typescriptlang.org/docs/

---

Python — RAG Service:

                 Library                                      URL                      
   FastAPI                               https://fastapi.tiangolo.com/tutorial/first-steps/                
   Uvicorn (ASGI server)                 https://www.uvicorn.org/                      
   fastembed (local ONNX embeddings)     https://qdrant.github.io/fastembed/           
   rank-bm25 (BM25Plus lexical search)   https://github.com/dorianbrown/rank_bm25      
   numpy (in-memory vector index)        https://numpy.org/doc/stable/                 
   asyncpg (async PostgreSQL)            https://magicstack.github.io/asyncpg/current/ 
   httpx (async HTTP client)             https://www.python-httpx.org/                 
   ChromaDB (originally used, replaced)  https://docs.trychroma.com/                   
   pytest-asyncio                        https://pytest-asyncio.readthedocs.io/    

---

 Python — Speech-to-Text Service:

               Library                                 URL                     
   faster-whisper                   https://github.com/SYSTRAN/faster-whisper  
   OpenAI Whisper (original model)  https://openai.com/research/whisper        

---
   Go — LLM Interface Service:
┐
                  Library                                    URL                    
   gorilla/mux (HTTP router)              https://github.com/gorilla/mux            
   godotenv                               https://github.com/joho/godotenv          
   golang.org/x/time/rate (rate limiter)  https://pkg.go.dev/golang.org/x/time/rate 
   Go net/http                            https://pkg.go.dev/net/http               
   Go sync (RWMutex, etc.)                https://pkg.go.dev/sync                   

  ---
  Frontend (SvelteKit stack):
                                                                                 
   SvelteKit            https://kit.svelte.dev/docs                              
   Svelte 5             https://svelte.dev/docs                                                           
   Prisma (ORM)         https://www.prisma.io/docs                               
   better-auth          https://www.better-auth.com/docs                         
   Vite                 https://vitejs.dev/guide/                                                                  

  ---
  Infrastructure:
                                                               
     Docker                     https://docs.docker.com/         
     Docker Compose             https://docs.docker.com/compose/ 
     Ollama (local LLM server)  https://ollama.com/              
     PostgreSQL                 https://www.postgresql.org/docs/ 
     Caddy (reverse proxy)      https://caddyserver.com/docs/    

  ---
  Theory:
                        Concept                                                        URL                                 
     RAG — original paper					             https://arxiv.org/abs/2005.11401                                    
     BM25 — Okapi BM25                                   https://en.wikipedia.org/wiki/Okapi_BM25                                             
     Cosine similarity                                   https://en.wikipedia.org/wiki/Cosine_similarity                     
     HNSW (what ChromaDB uses, and why it was replaced)  https://arxiv.org/abs/1603.09320                                    
     Whisper — ASR paper			                     https://arxiv.org/abs/2212.04356                                    
     Server-Sent Events (Go streaming)                   https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events 
     Token bucket (rate limiting)                        https://en.wikipedia.org/wiki/Token_bucket                          
  
  




