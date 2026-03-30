Svelte is a UI framework like React or Vue, but with a key difference: instead of running a virtual DOM in the browser at runtime, Svelte compiles your components into plain, optimized JavaScript at build time. The result is smaller bundles and faster apps — there's no Svelte "runtime" shipped to the browser.
Here's a quick mental model:
React/Vue → ships a runtime library → does DOM diffing in the browser
Svelte → compiles away at build time → ships plain JS that directly updates the DOM
--------------------

1. Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

source ~/.bashrc

nvm --version

nvm install --lts

npm install
npm run dev

npm install --save-dev vite
npm run dev
