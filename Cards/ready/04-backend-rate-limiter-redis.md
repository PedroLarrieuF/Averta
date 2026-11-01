---
id: 04
title: "Replace In-Memory Rate Limiter with Redis (slowapi)"
priority: critical
type: tech-debt
agent: backend
sprint: 1
estimate: M
status: ready
created: 2026-11-01
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
- [ ] Adicionar `slowapi` ao `pyproject.toml`
- [ ] Criar `app/core/rate_limit.py` com `RateLimiter` baseado em Redis
- [ ] Implementar sliding window log algorithm
- [ ] Configurar limites por endpoint (auth: 10/min, upload: 5/min, API: 100/min)
- [ ] Substituir `RateLimitDep` em `dependencies.py`
- [ ] Adicionar headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] Testes: unit (limiter logic), integração (multiple requests)
- [ ] Documentar configuração via env vars

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
- [ ] Rate limiting funciona corretamente com múltiplas instâncias
- [ ] Headers de rate limit nas respostas
- [ ] Limites configuráveis por endpoint
- [ ] Não quebra testes existentes
- [ ] Logs estruturados quando limit exceeded

## Referências
- `TECHLEAD_REVIEW.md` - TD-004, Security Review
- `backend/app/core/dependencies.py:163-199` - código atual
- slowapi docs: https://github.com/laurents/slowapi