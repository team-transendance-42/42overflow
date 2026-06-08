
  The generator has two distinct responsibilities that are worth
  separating:

  build_prompt(question, contexts) — pure string assembly, no I/O. Takes
   the top-k docs from hybrid_search and formats them into the prompt
  the LLM will read. Completely testable without Ollama running.
  --------

  generate(question, contexts) — the full pipeline: build prompt → POST
  to Ollama /api/chat → return answer string. This is where the LLM
  actually runs.

  -------
  Why "answer ONLY from context"?

  The system prompt tells the model to ground its answer in the
  retrieved docs rather than hallucinate from training weights. Without
  this instruction, a capable model will often give a confident-sounding
   answer that has nothing to do with your knowledge base. The
  constraint forces it to cite what it was given — and to say "I don't
  have enough context" when the retrieved docs don't cover the question.
   That honest failure is more useful than a confident hallucination.

  Prompt structure

  [System]   You are a helpful assistant for 42 school students.
             Use ONLY the context below to answer. If unsure, say so.

  [Context]  [1] Q: What is free()?
                 A: Releases heap memory...

             [2] Q: What causes a segfault?
                 A: Dereferencing a null pointer...

  [Question] explain why my program crashes after free()

  Numbering the context blocks lets the model reference them ("as shown
  in [1]...") and makes debugging easier — you can see which retrieved
  docs contributed to the answer.
  ----------------------

  