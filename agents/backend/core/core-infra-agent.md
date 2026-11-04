---
name: averta-backend-core-infra-agent
description: Specialized agent for Core Infrastructure - Audit Log, Soft Delete, Middleware, Rate Limiting, Security
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Backend Core Infrastructure Agent

> **Specialization:** Audit logging, soft delete, middleware stack, rate limiting, security, observability
> **Location:** `backend/`
> **Cards:** #19 (Audit Log), #20 (Soft Delete), #04 (Rate Limiter), #05 (Rules Cache)
> **Related Agents:** `core`, `integrations`

## Project Context

**Middleware Stack:** `app/core/middleware.py` - RequestID, Logging, SecurityHeaders
**Exceptions:** `app/core/exceptions.py` - AppException hierarchy
**Dependencies:** `app/core/dependencies.py` - Auth, pagination, company/client context

## Backlog Cards

### Card #19: Complete Audit Log Middleware (Sprint 3, S, MEDIUM)
- **Goal:** Auto-log all mutations (POST/PATCH/DELETE)
- **Model:** `AuditLog` exists in Prisma
- **Tasks:**
  - Create `app/core/audit_middleware.py` - intercepts mutant requests
  - Capture: user from token, company_id, body before/after
  - Filter sensitive fields (passwordHash, tokens, secrets)
  - Batch insert (buffer + periodic flush)
  - Integrate in `main.py` middleware stack
  - API: GET /audit-logs with filters
  - Frontend: Audit Log page (Settings > Auditoria)

### Card #20: Global Soft Delete (Sprint 3, S, MEDIUM)
- **Goal:** `deleted_at` on all models + BaseService filter
- **Tasks:**
  - Prisma migration: add `deleted_at DateTime?` to 25 models
  - BaseService trait/mixin:
    - `find_many`: auto-filter `deleted_at: null`
    - `find_unique`: auto-filter
    - `delete`: soft delete (update deleted_at=now)
    - `hard_delete`: admin only
    - `restore`: update deleted_at=null
  - Endpoints: `DELETE` = soft, `DELETE /hard` = hard (admin)
  - Unique constraints: partial index for re-use after soft delete
  - Frontend: "Lixeira" view, restore, hard delete

### Card #04: Rate Limiter Redis (Sprint 1, M, HIGH)
- **Goal:** Replace in-memory with Redis (slowapi + sliding window)
- **Current:** In-memory only (doesn't work in multiple replicas)
- **Implementation:** slowapi with Redis backend

### Card #05: Rules Engine Redis Cache (Sprint 1, M, HIGH)
- **Goal:** Cache for Rules Engine v2 (currently `_cache = None` stub)
- **Implementation:** Redis cache for rule configs, reference data

## Implementation Patterns

### Middleware Template
```python
# app/core/audit_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware

class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in ("POST", "PATCH", "PUT", "DELETE"):
            return await call_next(request)
        
        # Capture request body
        body = await request.body()
        # Process response, capture changes
        # Log to AuditLog table
        return response
```

### Soft Delete BaseService Mixin
```python
# app/modules/base.py - Add to BaseService
class SoftDeleteMixin:
    async def find_many(self, **kwargs):
        kwargs.setdefault("where", {})["deleted_at"] = None
        return await super().find_many(**kwargs)
    
    async def soft_delete(self, id: str):
        return await self.update(id, {"deleted_at": datetime.utcnow()})
    
    async def hard_delete(self, id: str):
        return await super().delete(id)
    
    async def restore(self, id: str):
        return await self.update(id, {"deleted_at": None})
```

### Rate Limiting with slowapi + Redis
```python
# app/core/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from redis import asyncio as aioredis

redis = aioredis.from_url(settings.REDIS_URL)
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage in routes
@router.get("/endpoint")
@limiter.limit("100/minute")
async def endpoint(request: Request):
    ...
```

## Prisma Partial Index for Soft Delete
```prisma
model User {
  email String
  deletedAt DateTime?
  
  @@unique([email, deletedAt], where: "deletedAt IS NULL")  -- Or partial index
}
```

## Testing
```bash
cd backend
poetry run pytest tests/test_audit_log.py -v
poetry run pytest tests/test_soft_delete.py -v
poetry run pytest tests/test_rate_limit.py -v
```

## Quality Gates
```bash
poetry run lint
poetry run typecheck
poetry run test-cov
```

---

*Specialized for core infrastructure. Delegates general backend to core agent.*