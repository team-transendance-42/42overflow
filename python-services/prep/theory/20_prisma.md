 What is Prisma?
  
  Prisma is an ORM (Object-Relational Mapper). The problem it solves: databases speak SQL, JavaScript speaks objects. Prisma is the translator.

  Without Prisma you'd write:
  SELECT * FROM "Post" WHERE "userId" = $1 AND "deleted_at" IS NULL

  With Prisma you write:
  db.post.findMany({ where: { userId: '...', deleted_at: null } })

  Same result, but typed, safe, and refactorable.

  =======================================
   How Prisma works — 3 layers

  Layer 1: schema.prisma — the source of truth

  Your file at prisma/schema.prisma is a description of your database in Prisma's own language. It has three sections:

  generator client {       // ← what to generate (JS client)
    provider = "prisma-client-js"
  }

  datasource db {          // ← which database and where
    provider = "postgresql"
    url      = env("DATABASE_URL")
  }

  model Post { ... }       // ← your tables

==================================
 Layer 2: Code generation

  When you run prisma generate, Prisma reads schema.prisma and generates TypeScript code into node_modules/.prisma/client/. This generated code is
  what gives you autocomplete — db.post.findMany() is a real typed function, not magic.

  schema.prisma  →  prisma generate  →  node_modules/.prisma/client/
                                            (typed JS/TS code)

  Layer 3: Migration / push

  Two ways to sync the schema to the real database:

  ┌────────────────────┬──────────────────────────────────────────┬────────────────────┐
  │      Command       │               What it does               │    When to use     │
  ├────────────────────┼──────────────────────────────────────────┼────────────────────┤
  │ prisma migrate dev │ Creates a SQL migration file, applies it │ Production / teams │
  ├────────────────────┼──────────────────────────────────────────┼────────────────────┤
  │ prisma db push     │ Applies schema directly, no files        │ Dev / prototyping  │
  └────────────────────┴──────────────────────────────────────────┴────────────────────┘

  Your project uses db push — look at your docker-compose.yml line 51:
  command: sh -c "npx prisma db push --accept-data-loss && npm run dev -- --host"
  Every time the container starts, it syncs the schema to the DB automatically.

  ---
  How the connection works in your project

  The chain is:

  schema.prisma
    url = env("DATABASE_URL")
         ↓
  docker-compose.yml (line 35):
    DATABASE_URL: "postgresql://postgres:postgres@postgres:5432/transcendance_db"
         ↓
    postgresql://  user:password  @hostname:port  /database
         ↓
  postgres container (the service named "postgres" in docker-compose)
    image: postgres:15
    port 5432 (internal), 5433 (your host machine)

  The app container talks to the postgres container by its Docker service name (@postgres:5432). They're on the same Docker network (app-net), so
  Docker resolves the hostname postgres automatically.

  Your db.ts file just instantiates PrismaClient — Prisma reads DATABASE_URL from the environment and opens a connection pool automatically.
================================
Your actual schema structure

  User ──< Session        (one user, many login sessions)
  User ──< Account        (one user, many OAuth providers: GitHub, Google)
  User ──< Post           (one user, many posts)
  User ──< Comment        (one user, many comments)
  User ──< Like
  User ──< Follow (×2)    ("Follower" and "Following" — self-referential)

  Post ──< Comment
  Post ──< Like

  Comment ──< Like
  Comment ──< Comment     (self-referential: "CommentThread" — nested replies)

  The Session and Account tables are owned by Better Auth — you declared them in the schema so Prisma manages them, but Better Auth controls what
  goes in them.

==================================

