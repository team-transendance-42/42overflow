schema.prisma:

  model QAPair {
    tags  String[]   ← THIS — native array
  }

  String[] — a column that stores an array of strings directly. MariaDB cannot do this. You'd have to create a separate tags table with a foreign
  key and do a JOIN every time you query. PostgreSQL stores ['sorting', 'chunk-sort', 'moulinette'] as a single column value.

  Same for ChromaDB under the hood — vector databases are often built on PostgreSQL with pgvector.

  ---
  How Prisma couples with both

  Prisma puts a layer of abstraction between your code and the database engine:

  Your JS code
       ↓
  Prisma Client  (generated from schema.prisma)
       ↓
  Prisma Query Engine  (translates to correct SQL dialect)
       ↓
  PostgreSQL  OR  MariaDB  OR  SQLite  OR  MongoDB

  You write this once in Prisma:
  prisma.user.findMany({ where: { active: true } })

  Prisma generates the right SQL for whichever DB you point it at.

  Switching DB is theoretically one line in schema.prisma:
  // PostgreSQL
  datasource db {
    provider = "postgresql"
    url      = env("DATABASE_URL")
  }
  
  // MariaDB/MySQL
  datasource db {
    provider = "mysql"
    url      = env("DATABASE_URL")
  }

  But — if you use PostgreSQL-only features (like String[]), switching breaks. Your schema uses arrays, so you're PostgreSQL-only now.
  ---
MariaDB  =  fast pickup truck — gets the job done, MySQL-compatible, simple
  PostgreSQL = precision engineering tool — slower to learn, but handles complex data correctly

  For a RAG system storing arrays of tags, embeddings metadata, and needing strict type safety — PostgreSQL is the correct choice. MariaDB would
  force you into workarounds for things PostgreSQL handles natively.