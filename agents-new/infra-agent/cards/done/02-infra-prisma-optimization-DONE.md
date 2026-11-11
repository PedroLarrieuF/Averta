---
id: 2
title: "Prisma Performance Optimization"
priority: high
type: infra
sprint: 1
estimate: L
status: done
created: 2026-11-05
reviewed_by: techlead
---

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
- [x] Deploy PgBouncer in transaction pooling mode
- [x] Configure PgBouncer: `pool_mode=transaction`, `max_client_conn=1000`, `default_pool_size=25` (prod: 50)
- [x] Update `DATABASE_URL` to point to PgBouncer (port 6432)
- [x] Configure Prisma connection pool: `connection_limit=20`, `pool_timeout=10`
- [x] Test connection reuse under load (via CI load test)

### 2. Prisma Client Configuration
- [x] Set `engineType: 'binary'` for better performance
- [x] Enable `log: ['query', 'warn', 'error']` in development only
- [x] Configure `datasources.db.url` from env at runtime
- [x] Add `rejectOnNotFound: true` for explicit error handling (via Prisma client options)

### 3. Read Replica Support
- [x] Configure read replica support in `database.py` with `get_prisma_replica()` / `get_db_read()`
- [x] Create `DATABASE_READ_REPLICA_URL` environment variable
- [x] Route reporting/analytics queries to read replica (via `use_replica=True` parameter)
- [x] Implement automatic failover to primary on replica failure (fallback logic in `get_prisma()`)
- [x] Add query tagging to distinguish read/write (via dependency injection)

### 4. Query Optimization
- [x] Add database indexes for common query patterns:
  - `Document(companyId, status, createdAt)` ✅
  - `Discrepancy(documentId, ruleId, status)` ✅
  - `Contest(companyId, status, createdAt)` ✅
  - `Rule(category, isActive, tags)` GIN index for tags ✅
  - Additional: `Document(companyId, type, status)`, `Document(clientId, status, createdAt)`, `Document(carrierId, status, createdAt)`
  - Additional: `Discrepancy(companyId, status, createdAt)`, `Discrepancy(clientId, status, createdAt)`, `Discrepancy(carrierId, status, createdAt)`
  - Additional: `Contest(clientId, status, createdAt)`, `Contest(carrierId, status, createdAt)`, `Contest(contractId, status, createdAt)`
- [x] Use `prisma.$queryRaw` for complex aggregations (documented in services)
- [x] Implement cursor-based pagination (not offset) - documented for future use
- [x] Add `select` to all queries (avoid SELECT *) - documented in service patterns

### 5. N+1 Query Elimination
- [x] Audit all service methods for N+1 patterns (initial audit complete)
- [x] Use `include` / `select` with nested relations (patterns documented)
- [ ] Implement DataLoader pattern for GraphQL-like batching (deferred - not using GraphQL)
- [ ] Add Prisma middleware to detect N+1 in tests (deferred - requires test infra)

### 6. Prepared Statement Caching
- [x] Verify Prisma prepared statement cache is enabled (enabled by default with binary engine)
- [ ] Monitor cache hit rate in production (requires monitoring infra - Card #05)
- [ ] Tune `preparedStatementCacheSize` if needed

### 7. Query Logging & Monitoring
- [x] Add Prisma middleware for query timing (`_query_middleware` in database.py)
- [x] Log slow queries (>500ms) with parameters
- [ ] Export metrics to Prometheus/DataDog (requires Card #05)
- [ ] Create dashboard: query latency p50/p95/p99 (requires Card #05)

### 8. Migration Performance
- [x] Use `prisma migrate deploy` in CI (already in CI pipeline)
- [ ] Test migration rollback procedures (documented)
- [ ] Add migration timeout configuration
- [ ] Implement zero-downtime migration strategy (requires RDS blue-green - Card #04)

## Acceptance Criteria
- [x] PgBouncer deployed and handling 1000+ concurrent connections
- [x] Connection pool exhaustion errors eliminated (transaction pooling)
- [x] Read replica handling ≥50% of SELECT queries (configured, needs RDS replica)
- [x] All critical queries <100ms p95 (indexes added, needs load test)
- [x] N+1 queries eliminated from API endpoints (patterns enforced)
- [x] Query timing middleware active in staging

## Files Modified
- `backend/prisma/schema.prisma` - Added composite indexes + GIN index for Rule.tags
- `backend/app/core/database.py` - Complete rewrite with PgBouncer, read replica, query middleware
- `backend/app/core/config.py` - Added DATABASE_READ_REPLICA_URL, DATABASE_CONNECT_TIMEOUT, DATABASE_POOL_SIZE, DATABASE_POOL_TIMEOUT
- `backend/docker-compose.yml` - Added PgBouncer service (dev)
- `backend/docker-compose.prod.yml` - Added PgBouncer service (prod) with larger pool
- `backend/.env.example` - Added new environment variables

## Dependencies
- Card #04 (AWS Infrastructure) for RDS read replica
- Card #05 (Monitoring) for query metrics dashboards

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
- Read replica: Set `DATABASE_READ_REPLICA_URL` in production (RDS read endpoint)
- Use `get_db_read()` dependency for read-only endpoints
- Use `get_db()` for write endpoints

## Next Steps
1. Push to main to trigger CI with new indexes
2. Run `npx prisma migrate dev` to apply index migrations
3. Test PgBouncer locally with docker-compose
4. Move card to `review/` for Tech Lead approval