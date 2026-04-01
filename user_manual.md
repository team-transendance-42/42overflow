Svelte is a UI framework like React or Vue, but with a key difference: instead of running a virtual DOM in the browser at runtime, Svelte compiles your components into plain, optimized JavaScript at build time. The result is smaller bundles and faster apps — there's no Svelte "runtime" shipped to the browser.
Here's a quick mental model:
React/Vue → ships a runtime library → does DOM diffing in the browser
Svelte → compiles away at build time → ships plain JS that directly updates the DOM
--------------------

1. Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

source ~/.bashrc

nvm --version

//Installs latest LTS (Long Term Support) version of Node.js.
nvm install --lts

//Installs all project dependencies listed in package.json.
npm install

//Install Vite as a development dependency (if not already in package.json).
npm install --save-dev vite
---------------

2. Run everytime
npm run dev


// for ai assist in /go-backend:
3. Run go server to make req to ai api(hide the api key)
go run server.go

4. open browser
http://localhost:5173/ai-assist
