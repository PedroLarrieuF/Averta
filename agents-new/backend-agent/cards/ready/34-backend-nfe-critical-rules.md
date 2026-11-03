---
id: 34
title: "Implement NF-e Critical Rules (5 rules)"
priority: critical
type: feature
agent: backend
sprint: 3
estimate: L
status: ready
created: 2026-11-03
reviewed_by: techlead
dependencies: ["28", "30"]
---

# Card #34: Implement NF-e Critical Rules

## Description
Implement the 5 CRITICAL priority NF-e audit rules defined in RuleCode enum but not yet implemented in rules_critical.py.

## Rules to Implement

### 1. NFE_ICMS_CALCULO (CRITICAL)
- **Description**: Validate ICMS calculation on NF-e
- **Logic**: Verify ICMS base, aliquota, and value match expected calculations per UF
- **Cache TTL**: 1800s (30 min)

### 2. NFE_ICMS_ST (CRITICAL) 
- **Description**: Validate ICMS Substituição Tributária on NF-e
- **Logic**: Check ST calculation for products subject to ST regime
- **Cache TTL**: 1800s (30 min)

### 3. NFE_DIFAL (CRITICAL)
- **Description**: Validate DIFAL (Diferencial de Alíquota) for interstate operations
- **Logic**: Calculate DIFAL when UF origem != UF destino for non-Simples Nacional
- **Cache TTL**: 1800s (30 min)

### 4. NFE_FRETE_NA_BASE (CRITICAL)
- **Description**: Validate freight included in ICMS base calculation
- **Logic**: Check if freight value is correctly included in ICMS base per legislation
- **Cache TTL**: 1800s (30 min)

### 5. NFE_CTE_CROSS (CRITICAL)
- **Description**: Cross-validation between NF-e and CTE data
- **Logic**: Match NF-e with corresponding CTE (chave de acesso, valores, pesos)
- **Cache TTL**: 1800s (30 min)

## Acceptance Criteria

### Implementation
- [ ] Create rule classes in `backend/app/services/rules_critical.py`
- [ ] Register rules in `_load_builtin_rules()` in `rules_engine_v2.py`
- [ ] Each rule extends `BaseRule` with proper `evaluate()` method
- [ ] Return `DiscrepancyResult` with correct rule_code, rule_name, discrepancy_type

### Testing
- [ ] Unit tests for each rule (triggered/not triggered/edge cases)
- [ ] Integration tests with RulesEngineV2
- [ ] Cache behavior tests (TTL 1800s)
- [ ] All 34 existing tests still pass

### Quality Gates
- [ ] `python -m pytest tests/test_rules_critical.py -v` passes
- [ ] `python -m pytest tests/test_rules_critical.py::TestNFECriticalRules -v` passes (new tests)
- [ ] `python -m ruff check .` no new errors
- [ ] `python -m mypy .` passes

## Technical Details

### Files to Modify
1. `backend/app/services/rules_critical.py` - Add 5 new rule classes
2. `backend/app/services/rules_engine_v2.py` - Register in `_load_builtin_rules()`
3. `backend/tests/test_rules_critical.py` - Add test class `TestNFECriticalRules`

### Rule Template
```python
class NFEICMSCalculoRule(BaseRule):
    rule_code = RuleCode.NFE_ICMS_CALCULO
    rule_name = "Validação Cálculo ICMS NF-e"
    tags = {"nfe", "icms", "critical"}
    cache_ttl = 1800

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        # Implementation here
        pass
```

## References
- RuleCode enum: `backend/app/services/rules_engine_v2.py:36-41`
- Existing rules pattern: `backend/app/services/rules_critical.py`
- Test patterns: `backend/tests/test_rules_critical.py`

## Definition of Done
- [ ] 5 rule classes implemented and registered
- [ ] Unit tests for all 5 rules (≥3 tests each = 15 new tests)
- [ ] All 49 tests pass (34 existing + 15 new)
- [ ] Card moved to `review/`