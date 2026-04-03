To get your "Zombie Kittens" talking to Gemini, you need to bridge the gap between your Svelte frontend and the Google AI Go SDK on your backend.

You need to install the Google Generative AI SDK and set up a route that listens for your Svelte fetch request.

// run from llm-system-interface directory
go get github.com/google/generative-ai-go/genai
go get google.golang.org/api/option