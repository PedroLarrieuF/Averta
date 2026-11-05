# Card #02 - Prisma Performance Optimization

## Overview
Optimize Prisma ORM performance for production scale. Current implementation works but lacks connection pooling, query optimization, and read replica support needed for high-throughput freight audit processing.

## Priority: HIGH
## Estimate: L (Large)

## Current State
- Prisma schema with 100+ models
- Prisma Client generated and used in backend
- Direct connections to PostgreSQL (no pooling)
- Basic query patterns in services

## Required Work

### 1. Connection Pooling (PgBouncer)
- [ ] Deploy PgBouncer in transaction pooling mode
- [ ] Configure PgBouncer: `pool_mode=transaction`, `max_client_conn=1000`, `default_pool_size=25`
- [ ] Update `DATABASE_URL` to point to PgBouncer (port 6432)
- [ ] Configure Prisma connection pool: `connection_limit=20`, `pool_timeout=10`
- [ ] Test connection reuse under load

### 2. Prisma Client Configuration
- [ ] Set `engineType: 'binary'` for better performance
- [ ] Enable `log: ['query', 'warn', 'error']` in development only
- [ ] Configure `datasources.db.url` from env at runtime
- [ ] Add `rejectOnNotFound: true` for explicit error handling

### 3. Read Replica Support
- [ ] Configure RDS read replica
- [ ] Create `PrismaReadReplica` client instance
- [ ] Route reporting/analytics queries to read replica
- [ ] Implement automatic failover to primary on replica failure
- [ ] Add query tagging to distinguish read/write

### 4. Query Optimization
- [ ] Add database indexes for common query patterns:
  - `Document(companyId, status, createdAt)`
  - `Discrepancy(documentId, ruleId, status)`
  - `Contest(companyId, status, createdAt)`
  - `Rule(category, isActive, tags)` (GIN index for tags)
- [ ] Use `prisma.$queryRaw` for complex aggregations
- [ ] Implement cursor-based pagination (not offset)
- [ ] Add `select` to all queries (avoid SELECT *)

### 5. N+1 Query Elimination
- [ ] Audit all service methods for N+1 patterns
- [ ] Use `include` / `select` with nested relations
- [ ] Implement DataLoader pattern for GraphQL-like batching
- [ ] Add Prisma middleware to detect N+1 in tests

### 6. Prepared Statement Caching
- [ ] Verify Prisma prepared statement cache is enabled
- [ ] Monitor cache hit rate in production
- [ ] Tune `preparedStatementCacheSize` if needed

### 7. Query Logging & Monitoring
- [ ] Add Prisma middleware for query timing
- [ ] Log slow queries (>500ms) with parameters
- [ ] Export metrics to Prometheus/DataDog
- [ ] Create dashboard: query latency p50/p95/p99

### 8. Migration Performance
- [ ] Use `prisma migrate deploy` in CI (not dev)
- [ ] Test migration rollback procedures
- [ ] Add migration timeout configuration
- [ ] Implement zero-downtime migration strategy

## Acceptance Criteria
- [ ] PgBouncer deployed and handling 1000+ concurrent connections
- [ ] Connection pool exhaustion errors eliminated
- [ ] Read replica handling ≥50% of SELECT queries
- [ ] All critical queries <100ms p95
- [ ] N+1 queries eliminated from API endpoints
- [ ] Query timing middleware active in staging

## Files to Modify
- `backend/prisma/schema.prisma` (add indexes)
- `backend/app/db/prisma_client.py` (pool config, read replica)
- `backend/app/core/config.py` (new env vars)
- `docker-compose.yml` / `docker-compose.prod.yml` (PgBouncer service)
- `.github/workflows/ci.yml` (migration test)

## Dependencies
- Card #04 (AWS Infrastructure) for RDS read replica
- Card #01 (Docker Hardening) for PgBouncer container

## Notes
- PgBouncer config example:
  ```ini
  [databases]
  averta = host=postgres port=5432 dbname=averta user=averta password=xxx
  
  [pgbouncer]
  pool_mode = transaction
  max_client_conn = 1000
  default_pool_size = 25
  reserve_pool_size = 5
  ```
- Prisma connection limit formula: `pool_size = (cpu_cores * 4) + 1` for transaction pooling
- Monitor: `pg_stat_activity` for connection count, `pg_stat_statements` for query stats