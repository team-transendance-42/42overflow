Think of rate limiter like a candy machine.

The machine has a bucket that can hold up to b candies.
At start, bucket is full.
Every time someone asks for candy, 1 candy is removed.
New candies are added slowly at speed r candies per second.
If no candy is left, you must wait or be denied.
That is exactly token bucket.

What r and b mean

r is the normal speed limit.
Example: r = 2 means about 2 requests each second forever.
b is burst size.
Example: b = 5 means you can do a quick burst of 5 requests at once before slowdown.

Three main actions

Allow:
Asks now, instantly.
If token exists, yes.
If not, no.
Good for quick reject with 429.

Reserve:
Asks now, gets answer like:
You can do it, but wait 700 ms.
Good when you want to schedule future action.

Wait:
Asks now and pauses until token is ready.
If context is canceled, it stops waiting.
Good for queue-like behavior.
===

Allow = try now, maybe fail
Reserve = book a future slot
Wait = stand in line
What zero value means

Empty limiter with no setup.
It blocks everything.
So you should create limiter with NewLimiter.

Why it says safe for many goroutines

Many users can hit same limiter at same time.
Package handles locking internally.
You do not need extra lock around Allow on same limiter object.
===

Tiny example
Suppose:

r = 10 tokens per second
b = 20
Then:

At start, 20 quick requests can pass.
After bucket empties, only about 10 requests each second can continue.
Extra requests get denied or delayed depending on method.
===

Stops student spam.
Lowers chance of Gemini 429.
Keeps app fair for all users.
Prevents sudden cost spikes.
Super simple rule to remember
Rate limiter is a speed governor:
You can run fast for a short burst, but average speed stays controlled.
=======================================================================================================
For an LLM proxy, rate limiting is not optional. It is the core control for fairness, cost, and uptime.
=======================================================================================================
Free Gemini is usually not suitable for sustained 500 requests per minute.
You should design for strict per-student quotas plus a global gateway cap.
Start conservative, measure real upstream behavior, then tune.
What 500 requests per minute really means

500 rpm is about 
8.3
8.3 requests per second.
If average stream lasts 15 to 25 seconds, required concurrency is large.
Using Little's Law: concurrency ≈ λ x W
With λ=8.3/s and W=20s, concurrency is about 166 166 active streams.
That is typically far above free-tier comfort.
So yes, 500 rpm at the app edge can be possible, but not if every request calls free Gemini directly in real time.
====

What policy is best for a school project
Use 3 layers at the same time.

*** Per-student limits: ***
Set both short-window and daily quota.
Example policy:
2 requests per minute
burst 2
20 requests per day
This is usually much better than 5 per day or 1 per hour.
5 per day is often too restrictive for learning.
1 per hour kills normal usage flow.

*** Global limits: ***
Protect server and upstream quota.
Example policy:
60 requests per minute global cap
burst 20
max in-flight Gemini streams 10 to 20


