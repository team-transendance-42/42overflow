Quick notes for Prisma + Postgres with Docker

1. Start Postgres and app (dev):

```bash
# start postgres + app in dev container (live-reload)
docker compose up --build
```

2. Run Prisma inside the container:

```bash
# get a shell inside the running app container
docker compose exec app sh
# then run inside container
npx prisma migrate dev --name init
```

3. Environment
- Copy `.env.example` to `.env` and adjust `DATABASE_URL` if necessary.

4. Notes
- The Prisma schema is at `prisma/schema.prisma`.
- If you use Prisma 4->7 migration changes, you may need to adapt the schema datasource handling. See Prisma docs.




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
