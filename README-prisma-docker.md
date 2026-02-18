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
