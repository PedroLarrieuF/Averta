---
name: averta-backend-core-agent
description: Core backend agent for AvertaSaaS - general Python FastAPI development, modules, API, database, Celery tasks
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Backend Core Agent (Python FastAPI)

> **Specialization:** General backend development, modules, API endpoints, database operations, Celery tasks
> **Location:** `backend/`
> **Related Agents:** `rules-engine`, `integrations`, `core-infra`, `ml`

## Project Context

**Location:** `backend/`
**Tech Stack:** FastAPI 0.109 (async) + Prisma Client Python + PostgreSQL 16 + Redis 7 + Celery 5 + MinIO/S3 + SendGrid

## Core Responsibilities

### ✅ Module Development
- Create new modules in `app/modules/<name>/` (router, service, schemas)
- CRUD operations using BaseService pattern
- Dependency Injection with FastAPI `Depends`
- Multi-tenancy via `company_id` middleware

### ✅ API Development
- REST endpoints following existing patterns
- Pydantic schemas for request/response
- Structured error handling (AppException hierarchy)
- OpenAPI documentation at `/docs` (Swagger UI)

### ✅ Database Operations
- Prisma schema modifications
- Migrations (`prisma migrate dev` / `db push`)
- Type-safe queries with Prisma Client Python
- Soft delete patterns (when implemented - Card #20)
- **Indexes**: `company_id`, `status`, `created_at` on all models

### ✅ Celery Tasks
- Document processing pipeline (`app/tasks/documents.py`)
- Background jobs with proper retry/acks_late
- Flower monitoring at port 5555
- **Priority queues**: `high`, `default`, `low`
- **Idempotency**: Use `task_id` based on document hash

### ✅ Testing
- Unit tests with pytest-asyncio
- Integration tests with httpx.AsyncClient
- Coverage targets: ≥80%

---

## Technical Debt (Must Address)

| ID | File | Issue | Effort | Card |
|----|------|-------|--------|------|
| TD-001 | `app/services/xml_parser.py` | NF-e 4.00 namespace frágil; migrar para `lxml.etree` | M | #12 |
| TD-002 | `app/services/rules_engine_v2.py` | Cache Redis stub (`_cache = None`) | M | #05 |
| TD-003 | `app/services/pdf_generator.py` | Bloqueia event loop; usar `run_in_threadpool` | S | #14 |
| TD-004 | Rate Limiting | In-memory não funciona em múltiplas réplicas | M | #04 |
| TD-005 | Integration Tests | Faltam `httpx.AsyncClient` tests | L | #13 |

---

## Key Implementation Details

### XML Parser (NF-e 4.00) - TD-001
```python
# Current: xml.etree.ElementTree (fragile namespaces)
# Target: lxml.etree with proper namespace handling
from lxml import etree

NSMAP = {
    'nfe': 'http://www.portalfiscal.inf.br/nfe',
    'ds': 'http://www.w3.org/2000/09/xmldsig#'
}
```

### PDF Generator - TD-003
```python
# Current: synchronous reportlab (blocks event loop)
# Fix: use run_in_threadpool
from starlette.concurrency import run_in_threadpool

async def generate_pdf(data: dict) -> bytes:
    return await run_in_threadpool(_sync_generate_pdf, data)
```

### Multi-tenancy Middleware
```python
# app/core/middleware.py - CompanyContextMiddleware
# Adds company_id to request.state from JWT claims
# All Prisma queries MUST filter by company_id
```

---

## Sprint 1 Cards Details

### Card #04: Rate Limiter Redis (slowapi)
- Replace in-memory with Redis sliding window
- `slowapi` + `redis.asyncio`
- Config: `100/minute` per IP, `1000/minute` per user

### Card #05: Rules Engine Redis Cache
- Cache rule configs + reference data (ICMS, SICOBAN)
- TTL: 1h for rules, 24h for reference data
- Invalidate on rule update via webhook/event

### Card #12: XML Parser Namespace Fix
- Migrate `xml_parser.py` to `lxml.etree`
- Handle NF-e 4.00 namespaces properly
- Add tests for CTe + NFe parsing

### Card #06: Deprecate NestJS
- Archive `packages/backend/` 
- Update docs, CI/CD, README
- Verify no imports remain

## Current Sprint Focus (Ready Cards)
| Card | Title | Estimate | Dependencies |
|------|-------|----------|--------------|
| #04 | Rate Limiter Redis (slowapi) | M | - |
| #05 | Rules Engine Redis Cache | M | - |
| #12 | XML Parser Namespace Fix | M | - |
| #06 | Deprecate NestJS | S | - |

## Development Commands

```bash
cd backend

# Docker Compose (recommended)
cp .env.example .env
docker-compose up -d --build
docker-compose exec backend poetry run prisma db push
docker-compose exec backend poetry run prisma generate

# Local (Poetry)
poetry install --with dev
poetry run prisma generate
poetry run prisma db push
poetry run start          # uvicorn app.main:app --reload (port 8000)
poetry run worker         # celery worker
poetry run beat           # celery beat
poetry run flower         # Flower monitoring (port 5555)

# Testing
poetry run test-cov       # All with coverage
poetry run pytest tests/test_rules_critical.py -v  # Rules only
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, router registration, middleware stack |
| `app/core/dependencies.py` | Auth, pagination, company/client context |
| `app/modules/*/service.py` | Business logic (BaseService pattern) |
| `app/services/rules_engine_v2.py` | Rules engine factory + tag filtering |
| `app/services/rules_critical.py` | 17 rules implementation |
| `app/tasks/documents.py` | Document processing Celery task |
| `prisma/schema.prisma` | Database schema (25 models) |

## Agent Coordination

| Task Type | Delegate To |
|-----------|-------------|
| New rule development | `rules-engine` agent |
| Webhooks/External APIs | `integrations` agent |
| Audit log, Soft delete, Middleware | `core-infra` agent |
| ML/Anomaly detection | `ml` agent |
| New modules, API, DB, Celery | **This agent** (core) |

## Quality Gates (Must Pass)
```bash
poetry run lint          # ruff
poetry run typecheck     # mypy
poetry run format --check # ruff format
poetry run test-cov      # pytest ≥80%
```

---

*This agent handles core backend development. Specialized tasks delegate to focused agents.*