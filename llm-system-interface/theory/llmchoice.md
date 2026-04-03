I chose Google Gemini:

Prros
Generous free tier (15 req/min)
1M token context window
No credit card required
Fast flash model

Cons
Go SDK less mature
REST API slightly more complex
Data used for training (free tier)
======================================================

Step 1 — Get the key (5 minutes, no card needed)The first step is to open Google AI Studio weDevs at aistudio.google.com, sign in with any Google account, and:
Accept Terms of Service on first visit — a default project and key are created automatically
In the left sidebar → API Keys
Click Create API Key → select your project
Copy the AIza... key immediately and store it somewhere safe — treat it like a password
A Gemini API key does not expire automatically — it stays active until you delete it, restrict it, or regenerate it manually.

===========

The three models available on the free tier are Gemini 2.5 Pro at 5 RPM and 100 requests per day, Gemini 2.5 Flash at 10 RPM and 250 daily requests, and Gemini 2.5 Flash-Lite which leads the pack at 15 RPM and 1,000 daily requests. All three share a 250,000 tokens-per-minute limit and full access to the 1-million-token context window. AI Free API
For a school project, use gemini-2.5-flash — best balance of speed, quality, and free quota.
One important heads-up: multiple keys inside one project still share the same free-tier quota bucket LaoZhang AI Blog, so creating extra keys doesn't give you more requests.























=======================================================
another close option is: Groq (Llama) - didnt like the interface: for basic short q, got reply: too long request
llama-3.3-70b · mixtral-8x7b
Docs
7.5
Free tier
9
Ease
8.5
Pros
✓ Fastest inference (~500 tok/s)
✓ Free tier, OpenAI-compatible API
✓ No card needed for free
✓ Open source models
Cons
✗ Tight daily rate limits (free)
✗ Smaller community vs OpenAI
✗ Less reliable uptime