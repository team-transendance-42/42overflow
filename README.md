# sv

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

# recreate this project template
```sh
npx sv create --template minimal --types ts --add prettier eslint tailwindcss="plugins:forms" mdsvex paraglide="languageTags:en, nl+demo:no" mcp="ide:vscode+setup:remote" --install npm ./
```

## Developing

Once you've created a project and installed dependencies with `npm install`, start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.
