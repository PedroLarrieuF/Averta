---
id: 05
title: "Implement Redis Cache in Rules Engine v2"
priority: high
type: tech-debt
agent: backend
sprint: 1
estimate: M
status: ready
created: 2026-11-01
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
- [ ] Adicionar `redis.asyncio` client no engine (ou usar global de `core/rate_limit.py`)
- [ ] Implementar cache key strategy: `rule:{rule_code}:{hash(context_relevant_fields)}`
- [ ] TTL configurável por regra (padrão: 1h; Sicoban: 24h; ICMS ST: 6h)
- [ ] Métodos: `_get_cached_result()`, `_set_cached_result()`
- [ ] Invalidar cache quando:
  - FreightTable atualizada
  - Reference data (icms_rules.json, sicoban_table.json) alterada
  - Deploy novo (version tag no cache key)
- [ ] Métricas: cache hit/miss logs
- [ ] Testes: cache hit, miss, invalidação, TTL expiry

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
- [ ] Cache hit rate > 80% para regras repetidas
- [ ] Latência regras cacheadas < 10ms
- [ ] Invalidação funciona ao atualizar tabelas
- [ ] Não quebra regras existentes
- [ ] Logs mostram hit/miss

## Referências
- `backend/app/services/rules_engine_v2.py:119-126` - engine structure
- `TECHLEAD_REVIEW.md` - TD-002
- `backend/app/data/` - reference data que invalida cache