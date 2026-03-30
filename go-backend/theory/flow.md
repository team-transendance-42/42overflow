1.run app:
npm run dev
------------------------------
2. run go server: (in go dir) to start the Go backend server that will handle API requests from the Svelte frontend and communicate with the Anthropic API. needed only for development, in production you would build the Go server and run the binary. this is needed only to hide your API key and add backend logic, since you should never call the Anthropic API directly from the frontend.

go run server.go
------------------------------
3. currently missing index.html, in browser:
http://127.0.0.1:5173/ai-assist
