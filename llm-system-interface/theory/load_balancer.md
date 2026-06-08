Sticky Sessions
=================================================
Normally a load balancer sends each request to any available server. The problem: your 10-question history lives in that server's memory. If user A talks to server 1, then gets routed to server 2 — history is gone.
Sticky sessions = the load balancer looks at a cookie (e.g. SESSION_ID), and always routes that cookie's owner to the same server. User A always hits server 1. Simple, no shared state needed.
===============================
Would a Load Balancer make a difference?
Yes, but only for the "App" and "LLM-Server" logic.

A load balancer (like Caddy) can distribute web traffic to multiple instances of your SvelteKit app.

However, it only helps the AI if you have multiple GPU machines running Ollama. If you have 5 instances of llm-server all pointing to one ollama container, you still have the same bottleneck at the GPU level.
=================================
on't worry about Load Balancing yet. Implement "Fair-Use Rate Limiting." * Create a logic where each student gets 2 AI questions per hour.

This proves you understand resource management—a critical skill when working with expensive AI tokens in a real company.
==================================



