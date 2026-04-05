Re-enable daily cap immediately.
Use authenticated user ID from session/JWT, not raw header.
Add global semaphore for active Gemini calls (for example 10-20 max).
Persist counters in Redis/Postgres for restart-safe and multi-instance consistency.
Skip rate limiting for OPTIONS.
Add exact Retry-After and consistent JSON error body.
Add metrics: 429 count, 503 count, active streams, upstream 429/503.
If you want, I can implement the next hardening patch now in this order:

Re-enable daily quota + skip OPTIONS.
Add global concurrency cap middleware/service guard.
Add accurate Retry-After and structured error response.
=======================================================



* set up for each user a limit: 2 ai q a day, 1 image generation day
* add a new endpoint for image generation, and a new function in services/llm.go
* add a new function in services/llm.go to call the Gemini image generation API
* add a new handler in handlers/handlers.go for the image generation endpoint, and call the new function in services/llm.go to get the image URL, then return it in the response

todo: 
in db create table user_limits with columns: user_id (string), date (date), ai_q_count (int), image_gen_count (int) and a unique constraint on (user_id, date) : connect to db and check the limits in the handlers before calling the services functions, and update the counts after successful calls
================

->> the page URL: http://127.0.0.1:5173/ai-assist
the API endpoint: /ai-assist

This URL in browser:

http://127.0.0.1:5173/ai-assist

is a page navigation, so it is GET /ai-assist.

Your backend route is not a page route. It is a POST API route.

Use different paths:

page: /ai-assist
API: /api/ai-assist
