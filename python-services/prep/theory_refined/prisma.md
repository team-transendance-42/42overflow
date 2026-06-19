Prisma is an ORM — Object Relational Mapper. It sits between the JavaScript/TypeScript code and the database.

Without Prisma you write raw SQL:
INSERT INTO "User" (name, email) VALUES ('Petya', 'p@42.fr')
SELECT * FROM "User" WHERE id = 1

With Prisma you write JavaScript:
prisma.user.create({ data: { name: 'Petya', email: 'p@42.fr' } })
prisma.user.findFirst({ where: { id: 1 } })

Prisma also manages the schema (schema.prisma) and generates the DB tables from it via prisma db push.
========================
