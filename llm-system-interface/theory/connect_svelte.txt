To get your "Zombie Kittens" talking to Gemini, you need to bridge the gap between your Svelte frontend and the Google AI Go SDK on your backend.

You need to install the Google Generative AI SDK and set up a route that listens for your Svelte fetch request.

// run from llm-system-interface directory
go get github.com/google/generative-ai-go/genai
go get google.golang.org/api/option
===========================================
An SDK (Software Development Kit)
===========================================
is a set of tools, libraries, and documentation that helps you connect your code to another service or platform easily.

For example, the Google Generative AI Go SDK lets your Go backend talk to Google’s AI models (like Gemini) without you having to write all the low-level code yourself.

Tutorial: Using the Google Generative AI Go SDK

Install the SDK in your Go project:
Open a terminal in your backend folder.
Run:
go get github.com/google/generative-ai-go/genai
go get google.golang.org/api/option
Import the SDK in your Go code:
Set up the client:
Send a prompt to Gemini:
resp, err := client.GenerateGeminiText(ctx, &genai.GenerateGeminiTextRequest{
    Prompt: "Hello, Gemini!",
})
if err != nil {
    // handle error
}
// resp contains the AI’s answer
Use the response in your app (send it to your Svelte frontend, etc.).
In your Go backend:
Create an HTTP route (e.g., /generate) that listens for POST requests from your Svelte app.
In the handler, read the prompt from the request, call Gemini using the SDK, and send the AI’s response back as JSON.
Example Go handler:

In your Svelte frontend:
Use fetch to send the user’s prompt to your backend and display the result.
let prompt = "Hello, Gemini!";
let result = "";

async function askGemini() {
  const res = await fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });
  const data = await res.json();
  result = data.result;
}
Call askGemini() when the user submits a question, and show result in your UI.
summary: Backend: Receives prompt, calls Gemini, returns answer as JSON.
Frontend: Sends prompt, gets answer, displays it.
