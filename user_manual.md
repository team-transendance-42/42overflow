Svelte is a UI framework like React or Vue, but with a key difference: instead of running a virtual DOM in the browser at runtime, Svelte compiles your components into plain, optimized JavaScript at build time. The result is smaller bundles and faster apps — there's no Svelte "runtime" shipped to the browser.
Here's a quick mental model:
React/Vue → ships a runtime library → does DOM diffing in the browser
Svelte → compiles away at build time → ships plain JS that directly updates the DOM

nvm (Node Version Manager) is a tool that lets you easily install, manage, and switch between multiple versions of Node.js on your system. This is useful if you need to use different Node.js versions for different projects or want to quickly upgrade or downgrade Node.js without affecting other setups.

npm (Node Package Manager) is the default package manager for Node.js. It is used to install, manage, and share JavaScript packages (libraries, tools, frameworks) for your projects. With npm, you can easily add dependencies, run scripts, and manage project configurations.

nvm is recommended to easily manage and switch Node.js versions, ensuring compatibility with Svelte and its tools.
npm is required to install Svelte, its dependencies, and development tools (like Vite) since Svelte projects rely on npm packages.
In summary: nvm is optional but helpful, while npm is essential for Svelte development.
--------------------

1. Install nvm (Node Version Manager) run the bash script after curl download
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

//apply any changes made to env variables, aliases, or functions—such as adding nvm to your PATH—without needing to open a new terminal window. 

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
