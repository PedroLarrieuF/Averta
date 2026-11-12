#!/bin/bash
# =============================================================================
# AvertaSaaS - Database Initialization Script
# Runs migrations and seeds database on container startup
# =============================================================================

set -e

echo "🚀 Starting AvertaSaaS database initialization..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h postgres -p 5432 -U postgres; do
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for PgBouncer to be ready
echo "⏳ Waiting for PgBouncer..."
until pg_isready -h pgbouncer -p 6432 -U postgres; do
  sleep 2
done
echo "✅ PgBouncer is ready!"

# Run Prisma migrations
echo "🔄 Running Prisma migrations..."
cd /app
npx prisma migrate deploy

# Check if database needs seeding (count companies)
COMPANY_COUNT=$(npx prisma db execute --stdin <<< "SELECT COUNT(*) FROM \"Company\";" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")

if [ "$COMPANY_COUNT" -eq 0 ]; then
  echo "🌱 Database is empty. Running seed script..."
  python prisma/seed.py
  echo "✅ Database seeded successfully!"
else
  echo "ℹ️ Database already has $COMPANY_COUNT companies. Skipping seed."
fi

echo "🎉 Database initialization complete!"