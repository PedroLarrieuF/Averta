---
id: 36
title: "Implement NF-e Medium Priority Rules (6 rules)"
priority: medium
type: feature
agent: backend
sprint: 3
estimate: M
status: ready
created: 2026-11-03
reviewed_by: techlead
dependencies: ["35"]
---

# Card #36: Implement NF-e Medium Priority Rules

## Description
Implement the 6 MEDIUM priority NF-e audit rules defined in RuleCode enum but not yet implemented.

## Rules to Implement

### 1. NFE_PESO_VOLUME (MEDIUM)
- **Description**: Validate weight/volume consistency on NF-e
- **Logic**: Check peso líquido/bruto vs volumes, cubage calculations
- **Cache TTL**: 7200s (2 hours)

### 2. NFE_COMPLEMENTAR (MEDIUM)
- **Description**: Validate complementary NF-e (carta de correção eletrônica)
- **Logic**: Check referenced NF-e exists, correction fields valid, within 720h
- **Cache TTL**: 7200s (2 hours)

### 3. NFE_CARTA_CORRECAO (MEDIUM)
- **Description**: Validate carta de correção (not complementary NF-e)
- **Logic**: Check correction letter fields, reason codes, authorization
- **Cache TTL**: 7200s (2 hours)

### 4. NFE_CANCELAMENTO (MEDIUM)
- **Description**: Validate NF-e cancellation rules
- **Logic**: Check cancellation within 24h, protocol, justification, no circulation
- **Cache TTL**: 7200s (2 hours)

### 5. NFE_INUTILIZACAO (MEDIUM)
- **Description**: Validate NF-e inutilization (numeração não utilizada)
- **Logic**: Check range validity, justification, no prior use, authorization
- **Cache TTL**: 7200s (2 hours)

### 6. NFE_REGIME_ESPECIAL (MEDIUM)
- **Description**: Validate special tax regime indicators
- **Logic**: Check CRT (Código de Regime Tributário) matches company regime
- **Cache TTL**: 7200s (2 hours)

## Acceptance Criteria

### Implementation
- [ ] Create 6 rule classes in `backend/app/services/rules_critical.py`
- [ ] Register rules in `_load_builtin_rules()` in `rules_engine_v2.py`
- [ ] Each rule extends `BaseRule` with proper `evaluate()` method
- [ ] Return `DiscrepancyResult` with correct rule_code, rule_name, discrepancy_type

### Testing
- [ ] Unit tests for each rule (triggered/not triggered/edge cases)
- [ ] Integration tests with RulesEngineV2
- [ ] Cache behavior tests (TTL 7200s)
- [ ] All existing + Card #34 + Card #35 tests still pass

### Quality Gates
- [ ] `python -m pytest tests/test_rules_critical.py -v` passes
- [ ] `python -m pytest tests/test_rules_critical.py::TestNFEMediumRules -v` passes (new tests)
- [ ] `python -m ruff check .` no new errors
- [ ] `python -m mypy .` passes

## Technical Details

### Files to Modify
1. `backend/app/services/rules_critical.py` - Add 6 new rule classes
2. `backend/app/services/rules_engine_v2.py` - Register in `_load_builtin_rules()`
3. `backend/tests/test_rules_critical.py` - Add test class `TestNFEMediumRules`

### Rule Template
```python
class NFEPesoVolumeRule(BaseRule):
    rule_code = RuleCode.NFE_PESO_VOLUME
    rule_name = "Validação Peso/Volume NF-e"
    tags = {"nfe", "peso", "volume", "medium"}
    cache_ttl = 7200

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        # Implementation here
        pass
```

## References
- RuleCode enum: `backend/app/services/rules_engine_v2.py:52-57`
- Existing rules pattern: `backend/app/services/rules_critical.py`
- Test patterns: `backend/tests/test_rules_critical.py`

## Dependencies
- Card #35: NF-e High Rules (must be done first)

## Definition of Done
- [ ] 6 rule classes implemented and registered
- [ ] Unit tests for all 6 rules (≥3 tests each = 18 new tests)
- [ ] All 88 tests pass (70 existing + 18 new)
- [ ] Card moved to `review/`