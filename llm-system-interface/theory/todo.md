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
