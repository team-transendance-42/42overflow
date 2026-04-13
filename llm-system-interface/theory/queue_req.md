When you have 42 students hitting one machine without a GPU, your CPU and RAM are the bottlenecks.

Ollama with NUM_PARALLEL=4: Ollama will try to split its "brain power" (CPU threads) into 4. If 4 people ask at once, each person gets 25% of the power. It feels slower, but they all see text moving at the same time.

The Problem: If student #5 arrives, they get a 503 Service Unavailable or a silent hang.

The Queue Solution: Instead of your app sending the question directly to Ollama, it puts it into a "Waiting Room" (the Queue).

Worker: A small script that sits between your app and Ollama. It asks: "Is Ollama busy?" If no, it takes the next person in line.

The State: The backend keeps track of the "Line Length." If you are #4 in line, the backend knows there are 3 people ahead.
i have only cpu, no gpu, so no parallel proccessing.
=======================================================

The "Conductor" Pattern
We are creating a Job Channel.

The Handlers (like GenerateOllamaText) don't call Ollama. They create a "Ticket" (Job) and drop it in the channel.

A Worker (a single Goroutine) sits in the background. It takes one ticket at a time, talks to Ollama, and marks it finished.

This ensures Ollama only ever processes one thing at a time, protecting your CPU.
============================================================
Rate Limiting is the bouncer at the door saying: "You can only enter twice a day." It protects your Gemini API wallet.

Queueing is the line for the bathroom inside: "Only one person can use the stall at a time." It protects your Local CPU/Ollama.
============================================================

Rate Limiter: Prevents one user from burning the 20/day Gemini quota.You run out of free AI credits in 5 minutes.
-----
Queue System: Prevents many users from crashing your CPU at the same time.Your WSL freezes, and 42 students get "Connection Timeout" because the CPU is at 100%.
==============================================================

Your current middleware is non-blocking. If 5 students are within their "2 per minute" limit and they all click "Ask" at the exact same second:

The middleware sees they have "tokens" available.
It lets all 5 requests through.
Your llm-server sends 5 simultaneous requests to Ollama.
Ollama (on CPU) tries to crunch 5 models at once.
Your machine crashes.
==============================================================
the easiest way to add a "Queue" without rewriting everything is a Semaphore. This limits how many goroutines can talk to Ollama at once.
================================================================

Implementing a Queue is the "industrial" way to handle hardware bottlenecks. Since you are on a CPU, this is the difference between a professional app and one that freezes your laptop.

1. The Logic: Rate Limiting vs. Queueing
Rate Limiting (Existing): "You can't ask more than 2 questions per minute." (Protects your Gemini API quota).

Queueing (New): "Ollama is busy. Please wait in line while the CPU finishes the previous student's work." (Protects your Local Hardware).
================================================================

Define the Queue: Create a global "channel" at the top of the file.

Acquire the Slot: At the very start of the function, try to put a "token" into the channel. If it's full, Go will automatically make the request wait in line.

Release the Slot: Use defer to ensure that even if the code errors out, the next student in line can still have their turn.
