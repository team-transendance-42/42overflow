#!/bin/bash
set -e

echo "Waiting for Postgres to be ready..."
until (echo > /dev/tcp/postgres/5432) 2>/dev/null; do
  echo "Postgres not ready, retrying in 2s..."
  sleep 2
done

echo "Postgres is up!"
npx prisma generate
npx prisma migrate deploy

echo "Database ready."
exec npm run dev -- --host
