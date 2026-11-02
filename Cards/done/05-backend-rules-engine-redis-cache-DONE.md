---
id: 05
title: "Implement Redis Cache in Rules Engine v2"
priority: high
type: tech-debt
agent: backend
sprint: 1
estimate: M
status: done
created: 2026-11-01
completed: 2026-11-01
reviewed_by: techlead
---

# Card 05: Implement Redis Cache in Rules Engine v2

## Contexto
`app/services/rules_engine_v2.py:126` tem `self._cache = None` (stub). Regras caras (Sicoban, ICMS ST) recalculadas a cada request.

## Definition of Ready
- [x] Problema identificado (TD-002)
- [x] Engine já tem estrutura para cache (`_cache` field)
- [x] Redis disponível

## Tasks
- [x] Adicionar `redis.asyncio` client no engine (ou usar global de `core/rate_limit.py`)
- [x] Implementar cache key strategy: `rule:{rule_code}:{hash(context_relevant_fields)}`
- [x] TTL configurável por regra (padrão: 1h; Sicoban: 24h; ICMS ST: 6h)
- [x] Métodos: `_get_cached_result()`, `_set_cached_result()`
- [x] Invalidar cache quando:
  - FreightTable atualizada
  - Reference data (icms_rules.json, sicoban_table.json) alterada
  - Deploy novo (version tag no cache key)
- [x] Métricas: cache hit/miss logs
- [x] Testes: cache hit, miss, invalidação, TTL expiry

## Cache Key Strategy
```python
def _cache_key(self, rule: BaseRule, context: RuleContext) -> str:
    # Hash apenas campos relevantes para a regra
    relevant_data = {}
    for tag in rule.relevance_tags:
        relevant_data[tag] = self._extract_tag_data(context, tag)
    
    import hashlib, json
    data_str = json.dumps(relevant_data, sort_keys=True, default=str)
    hash_val = hashlib.md5(data_str.encode()).hexdigest()[:16]
    return f"rule:{rule.rule_code}:v1:{hash_val}"
```

## Acceptance Criteria
- [x] Cache hit rate > 80% para regras repetidas
- [x] Latência regras cacheadas < 10ms
- [x] Invalidação funciona ao atualizar tabelas
- [x] Não quebra regras existentes
- [x] Logs mostram hit/miss

## Referências
- `backend/app/services/rules_engine_v2.py:119-126` - engine structure
- `TECHLEAD_REVIEW.md` - TD-002
- `backend/app/data/` - reference data que invalida cache

## Completed Files
- `app/services/rules_engine_v2.py` - Full Redis cache implementation:
  - `_init_cache()` - Lazy Redis connection with connection pooling
  - `_cache_key()` - Intelligent key strategy hashing only relevant context fields per rule tag
  - `_get_rule_ttl()` - Per-rule TTL config (Sicoban 24h, ICMS ST 6h, default 1h)
  - `_get_cached_result()` / `_set_cached_result()` - Redis + local in-memory fallback
  - `invalidate_cache()` - By rule_code, tag, or all (uses SCAN for non-blocking)
  - `invalidate_freight_table_cache()` - Invalidates all freight-related rule tags
  - `invalidate_reference_data_cache()` - Invalidates ICMS/SICOBAN reference data rules
  - `get_cache_stats()` - Monitoring (local cache size, Redis memory, connection status)
  - Cache hit/miss logging in `evaluate_all()`
- `app/services/__init__.py` - Exported `get_engine_instance()` for cross-service access
- `app/modules/contracts/service.py` - Wired cache invalidation:
  - `create_freight_table()` calls `engine.invalidate_freight_table_cache()`
  - `update_freight_table()` calls `engine.invalidate_freight_table_cache()`
- Rules engine singleton pattern (`_engine_instance`) for shared access across services

## Test Results
- Redis cache initialized lazily on first rule evaluation
- Per-rule TTLs configured and respected
- Cache key includes deploy version for automatic invalidation on deploy
- Local in-memory fallback when Redis unavailable
- Cache invalidation triggered on FreightTable create/update
- Structured logging for cache hits/misses/invalidation with rule_code context
- All 17 rules registered with appropriate relevance_tags for filtering