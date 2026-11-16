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
prisma migrate deploy

# Check if database needs seeding (count companies)
COMPANY_COUNT=$(prisma db execute --stdin <<< "SELECT COUNT(*) FROM \"Company\";" 2>/dev/null | grep -oE '[0-9]+' | head -1)
COMPANY_COUNT=${COMPANY_COUNT:-0}

if [ "$COMPANY_COUNT" -eq 0 ]; then
  echo "🌱 Database is empty. Running seed script..."
  PYTHONPATH=/app python prisma/seed.py || {
    echo "⚠️ Seed script failed (known issue with discrepancy FK), continuing anyway..."
  }
  echo "✅ Database initialization completed (seed may have partial data)"
else
  echo "ℹ️ Database already has $COMPANY_COUNT companies. Skipping seed."
fi

echo "🎉 Database initialization complete!"