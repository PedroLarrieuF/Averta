---
id: 04
title: "Replace In-Memory Rate Limiter with Redis (slowapi)"
priority: critical
type: tech-debt
agent: backend
sprint: 1
estimate: M
status: done
created: 2026-11-01
completed: 2026-11-01
reviewed_by: techlead
---

# Card 04: Replace In-Memory Rate Limiter with Redis

## Contexto
`app/core/dependencies.py:163-199` usa `RateLimiter` em memória (`self._cache: dict`). **Não funciona em múltiplas réplicas** (produção).

## Definition of Ready
- [x] Problema identificado no techlead review (TD-004)
- [x] Solução definida: `slowapi` + Redis sliding window
- [x] Redis já disponível no docker-compose

## Tasks
- [x] Adicionar `slowapi` ao `pyproject.toml`
- [x] Criar `app/core/rate_limit.py` com `RateLimiter` baseado em Redis
- [x] Implementar sliding window log algorithm
- [x] Configurar limites por endpoint (auth: 10/min, upload: 5/min, API: 100/min)
- [x] Substituir `RateLimitDep` em `dependencies.py`
- [x] Adicionar headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [x] Testes: unit (limiter logic), integração (multiple requests)
- [x] Documentar configuração via env vars

## Implementation Sketch
```python
# app/core/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
import redis.asyncio as redis

redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"]
)

# No main.py:
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

## Acceptance Criteria
- [x] Rate limiting funciona corretamente com múltiplas instâncias
- [x] Headers de rate limit nas respostas
- [x] Limites configuráveis por endpoint
- [x] Não quebra testes existentes
- [x] Logs estruturados quando limit exceeded

## Referências
- `TECHLEAD_REVIEW.md` - TD-004, Security Review
- `backend/app/core/dependencies.py:163-199` - código atual
- slowapi docs: https://github.com/laurents/slowapi

## Completed Files
- `app/core/rate_limit.py` - Redis-backed rate limiter with slowapi (sliding window)
- `app/core/dependencies.py` - Updated RateLimitDep for backward compatibility
- `app/main.py` - Rate limiter initialization and custom exception handler
- All module routers - Applied endpoint-specific limiters (`@auth_limiter`, `@upload_limiter`, `@api_limiter`, `@reports_limiter`, `@discrepancies_limiter`, `@contests_limiter`)

## Test Results
- Rate limiter initialized with Redis storage_uri for distributed limiting
- Sliding window algorithm configured
- Headers enabled: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Structured logging on rate limit exceeded events
- Endpoint-specific limits verified: auth (10/min), upload (5/min), API (100/min), reports (20/min), discrepancies (50/min), contests (30/min)