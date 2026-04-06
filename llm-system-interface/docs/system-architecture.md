ep 1:
HTTP Client Sends a POST request to /generate (Text) or /generate-image (Image).
===
Step 2:
main.go — HTTP Router net/http + gorilla/mux intercepts the request and matches it to the defined route handlers.
---------------------------------
Imagine you have a big jar of tokens (like coins or marbles). Every time you want to do something (like send a message or make a request), you have to take a token from the jar. If there are no tokens left, you have to wait until more tokens are added to the jar.

The "Token Bucket" is this jar. It slowly refills with tokens over time, but only up to a certain limit.
If you try to take a token when the jar is empty, you get blocked (like getting a "429 Too Many Requests" error).
The computer checks who you are (using your IP address or a special ID in your request) to see how many tokens you have left.
The "Sliding Window" is another way to count how many requests you made in the last few seconds or minutes, and blocks you if you go over the limit.
A store like Redis is just a fast place for the computer to remember how many tokens each person has, even if there are lots of people.

So, a rate limiter is like a fair game referee: it makes sure nobody can take too many turns too quickly, so the system doesn’t get overloaded.
------------------------------------
Both "Token Bucket" and "Sliding Window" are algorithms for rate limiting—controlling how many requests a user can make in a certain time.

Token Bucket: Imagine a bucket that fills with tokens at a steady rate. Each request takes a token. If the bucket is empty, requests are blocked. This allows bursts of requests up to the bucket size, but then slows down to the refill rate.
Sliding Window: This counts how many requests you made in the last X seconds/minutes. If you go over the allowed number in that window, you’re blocked. It’s stricter—no bursts, just a steady limit.
In Go, both can be implemented using maps, timers, and sometimes Redis for sharing limits across servers. There are libraries for both (like golang.org/x/time/rate for token bucket).
===
Step 3: Global Middleware Chain
3.1 Rate Limiter: (Token Bucket / Sliding Window) Checks user headers or IP against a store (like Redis) to allow or block (429) the request.

3.2 Request Parser: (json.Decoder) Extracts the raw JSON body into a Go struct.

3.3 Error Handler: A deferred recovery and logging middleware that ensures any downstream panic results in a clean JSON error response.
===
Step 4: Service Logic (The Branch)
Route A: LLM Text Service (/generate) * Integration: Initiates an SSE (Server-Sent Events) request to Gemini(or chosen LLM).

Action: The Stream Writer uses http.Flusher to push chunks to the client in real-time.

Output: text/event-stream (Type: Chunked SSE → client flush).

Route B: Image Gen Service (/generate-image) * Integration: Calls DALL·E or Stability API via standard http.Post.

Action: The JSON Response Writer waits for the full binary data or URL to return.

Output: application/json (Type: image_url or base64 bytes).
===

Step 5: Final Response Delivery
Text: The connection closes after the final "done" signal is sent via SSE.

Image: The HTTP body is written once with the full payload and the connection terminates.


