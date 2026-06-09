src/lib is SvelteKit's shared code folder. Anything here is importable from anywhere in the app using the $lib alias (e.g. import { db } from 
  '$lib/server/db'). Think of it as your project's internal library.
   It's split into 6 distinct concerns:

 src/lib/
  ├── server/          ← never reaches the browser
  │   ├── db.ts        ← PostgreSQL via Prisma
  │   └── auth.ts      ← session management
  ├── auth-client.ts   ← browser-side auth calls
  ├── zodTypes.ts      ← runtime validation schemas
  ├── fileUpload.ts    ← disk I/O for images
  ├── styles/          ← CSS variables (design system)
  ├── components/      ← reusable Svelte UI
  └── paraglide/       ← generated i18n code (don't edit)

  The server/ boundary is the key architectural rule: DB and auth logic never leak to the client.

  ---
  1. server/db.ts — Database connection (Prisma)
  
  What it is: A singleton PrismaClient instance — your connection to PostgreSQL.

  Why singleton: Node.js hot-reloads modules in dev. Without the singleton pattern, every reload would open a new DB connection until you exhaust
  the pool and crash. The globalThis.__prisma trick keeps one connection alive across reloads.

  Your code → db.user.findMany() → Prisma → SQL → PostgreSQL

  // Anywhere in server-side code:
  import { db } from '$lib/server/db';
  const users = await db.user.findMany();

  The server/ subfolder is special — SvelteKit blocks importing anything from $lib/server/* in client-side code. It's enforced at build time.

  ---
  2. server/auth.ts + auth-client.ts — Authentication (Better Auth)
  
  What it is: Two halves of the same auth system.

  ┌────────────────┬─────────────┬─────────────────────────────────────────────────────┐
  │      File      │   Runs on   │                       Purpose                       │
  ├────────────────┼─────────────┼─────────────────────────────────────────────────────┤
  │ server/auth.ts │ Server only │ Validates sessions, hashes passwords, handles OAuth │
  ├────────────────┼─────────────┼─────────────────────────────────────────────────────┤
  │ auth-client.ts │ Browser     │ Lets Svelte components call sign-in/sign-out        │
  └────────────────┴─────────────┴─────────────────────────────────────────────────────┘

  Better Auth is a self-hosted auth library. It uses Prisma as its database adapter, so user sessions are stored in your own PostgreSQL — you own
  the data.

  Supported login methods in your config:
  - Email + password
  - GitHub OAuth
  - Google OAuth

  Extra user fields you defined: first_name, last_name, biography, interests, last_seen, anonymize_at, deleted_at — Better Auth syncs these to its
  user table.
  ---
  3. zodTypes.ts — Input validation schemas
  
  What it is: Zod schemas that define the shape and rules of data coming from forms/API requests.

  Why Zod: TypeScript types exist only at compile time and vanish at runtime. Zod validates at runtime — when real user data arrives.

  // Schema = rules
  const CommentSchema = z.object({
    postId: z.number().int().positive(),
    content: z.string().min(1).max(500),
  });

  // Parse = validate + throw if invalid
  const data = CommentSchema.parse(formData);  // throws ZodError if bad
  // Or safely:
  const result = CommentSchema.safeParse(formData);  // returns { success, data, error }

  z.infer<typeof CommentSchema> extracts a TypeScript type from the schema so you don't define the type twice.

  ---
  4. fileUpload.ts — Image upload utility
  
  What it is: A single async function that saves uploaded images to static/uploads/images/ on disk.

  Flow:
  Browser File object
    → validate (type, size < 5MB)
    → generate UUID filename 
    → write to static/uploads/images/{uuid}.jpg
    → return URL: /uploads/images/{uuid}.jpg

  Files in static/ are served directly by SvelteKit as public assets, so the returned URL just works in <img src=...>.

  ---
  5. styles/tokens.css — Design tokens

  What it is: CSS custom properties (variables) that define your entire visual language in one place.

  :root {
    --color-primary-400: #d01515;   /* red */
    --space-md: 16px;
    --font-size-body: 16px;
  }

  Every component uses var(--color-primary-400) instead of hardcoded #d01515. Change the token once → updates everywhere. This is the same concept
  as design tokens in Figma or Tailwind's theme config.


