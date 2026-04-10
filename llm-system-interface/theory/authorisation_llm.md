The Technical Difference
OpenAI (Bearer Token): They use the HTTP Authorization Header. This is a standard way to send credentials where the "key" stays hidden from the URL logs. It looks like this in the background:
GET /v1/chat/completions HTTP/1.1
Authorization: Bearer YOUR_KEY

Gemini (Query Parameter): Google’s "API Key" system for AI Studio is designed to be simple. Instead of looking in the headers, their server looks at the URL string itself. By adding ?key=YOUR_KEY to the end of the address, the server identifies your account the moment the request hits the endpoint. This is more straightforward for users but less secure if you accidentally log the URL or share it. It looks like this:
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=YOUR_KEY