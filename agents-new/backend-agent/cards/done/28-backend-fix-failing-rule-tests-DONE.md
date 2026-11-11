---
id: 28
title: "Fix Failing Rule Tests"
priority: high
type: bug
agent: backend
sprint: 1
estimate: M
status: done
created: 2026-11-03
reviewed_by: techlead
---

# Card #28: Fix Failing Rule Tests

## Description
Fix 6 failing tests in `backend/tests/test_rules_critical.py` that are currently blocking the test suite from passing.

## Failing Tests

| Test | File | Likely Issue |
|------|------|--------------|
| `test_peso_real_vs_faturado` | `test_rules_critical.py` | Rule logic / tolerance calculation |
| `test_valor_minimo_frete` | `test_rules_critical.py` | ANTT table lookup / calculation |
| `test_cte_anulacao_without_ref` | `test_rules_critical.py` | CT-e complementar logic |
| `test_engine_cache_consistency` | `test_rules_critical.py` | Redis cache key generation |
| `test_rules_engine_integration` | `test_rules_critical.py` | Full audit flow |
| `test_rate_limit_import` | `tests/...` | `app.core.rate_limit` module import error |

## Acceptance Criteria

### Test 1: `test_peso_real_vs_faturado`
- [ ] Understand expected behavior: Peso Real vs Faturado rule triggers when difference > tolerance (5% for normal, 20% for granel)
- [ ] Fix rule implementation in `rules_critical.py` or fix test expectations
- [ ] Verify with known test cases

### Test 2: `test_valor_minimo_frete`
- [ ] Understand expected behavior: ANTT Resolution 5.839/2021 minimum freight calculation
- [ ] Fix rule implementation or test data
- [ ] Verify calculation: 3 eixos × 500km × 1.2 = 1470 (example)

### Test 3: `test_cte_anulacao_without_ref`
- [ ] Understand expected behavior: CT-e Anulação (tpEmis=3) requires reference CT-e
- [ ] Fix rule logic for complementary CT-e validation
- [ ] Test with and without reference CT-e

### Test 4: `test_engine_cache_consistency`
- [ ] Issue: Redis cache key generation inconsistency
- [ ] Fix cache key generation in `rules_engine_v2.py`
- [ ] Ensure same context produces same cache key

### Test 5: `test_rules_engine_integration`
- [ ] Full audit flow test failing
- [ ] Debug integration: document → parse → match contract → evaluate rules → create discrepancies
- [ ] Fix any step in the pipeline

### Test 6: `test_rate_limit_import`
- [ ] Import error: `from app.core.rate_limit import RateLimiter` fails
- [ ] Check if `app/core/rate_limit.py` exists
- [ ] Create module or fix import path

## Technical Requirements

### Files to Investigate/Modify
- `backend/app/services/rules_critical.py` - Rule implementations
- `backend/app/services/rules_engine_v2.py` - Engine + cache
- `backend/app/core/rate_limit.py` - Rate limit module (may need creation)
- `backend/tests/test_rules_critical.py` - Test file (fix expectations if needed)
- `backend/app/data/sicoban_table.json` - Reference data for ANTT values

### Debugging Steps
```bash
cd backend

# Run specific failing tests with verbose output
poetry run pytest tests/test_rules_critical.py::test_peso_real_vs_faturado -v
poetry run pytest tests/test_rules_critical.py::test_valor_minimo_frete -v
poetry run pytest tests/test_rules_critical.py::test_cte_anulacao_without_ref -v
poetry run pytest tests/test_rules_critical.py::test_engine_cache_consistency -v
poetry run pytest tests/test_rules_critical.py::test_rules_engine_integration -v

# Check rate limit module
ls -la app/core/rate_limit.py
poetry run python -c "from app.core.rate_limit import RateLimiter; print('OK')"
```

### Rule Implementation Patterns (from existing working tests)
```python
# Each rule extends BaseRule
class PesoRealVsFaturadoRule(BaseRule):
    code = "PESO_REAL_VS_FATURADO"
    name = "Peso Real vs Faturado"
    severity = DiscrepancySeverity.HIGH
    relevance_tags = {"weight"}

    def evaluate(self, context: RuleContext) -> list[DiscrepancyResult]:
        # Implementation
        pass
```

## Dependencies
- Card #04: Rate Limiter Redis (DONE - but module may not exist)
- Card #05: Rules Engine Redis Cache (DONE)
- Card #12: XML Parser Namespace Fix (DONE)

## Testing Requirements
- All 6 failing tests pass
- Full test suite passes: `poetry run test-cov`
- Coverage remains ≥80%
- No new failing tests introduced

## Definition of Done
- [ ] All 6 failing tests fixed and passing
- [ ] Full test suite: `poetry run test-cov` passes
- [ ] Coverage ≥80%
- [ ] Card moved to `review/`

## Notes
- Start with `test_rate_limit_import` - likely simplest (module missing)
- Then tackle rule logic tests one by one
- Use `poetry run pytest tests/test_rules_critical.py -v` to see all test output
- Check `backend/README.md` for rule specifications
- Reference data in `app/data/` may need updates for ANTT values