---
id: 35
title: "Implement NF-e High Priority Rules (7 rules)"
priority: high
type: feature
agent: backend
sprint: 3
estimate: L
status: ready
created: 2026-11-03
reviewed_by: techlead
dependencies: ["34"]
---

# Card #35: Implement NF-e High Priority Rules

## Description
Implement the 7 HIGH priority NF-e audit rules defined in RuleCode enum but not yet implemented.

## Rules to Implement

### 1. NFE_FCP (HIGH)
- **Description**: Validate FCP (Fundo de Combate à Pobreza) on interstate operations
- **Logic**: Calculate FCP when applicable (UF destino has FCP, non-Simples Nacional)
- **Cache TTL**: 3600s (1 hour)

### 2. NFE_CFOP_FRETE (HIGH)
- **Description**: Validate CFOP for freight operations
- **Logic**: Check CFOP matches freight type (CIF/FOB) and interstate/intrastate
- **Cache TTL**: 3600s (1 hour)

### 3. NFE_CFOP_INTERSTADUAL (HIGH)
- **Description**: Validate CFOP for interstate operations
- **Logic**: Ensure CFOP starts with 6.xxx for interstate sales/transfers
- **Cache TTL**: 3600s (1 hour)

### 4. NFE_NCM_CEST (HIGH)
- **Description**: Validate NCM/CEST pairing on NF-e items
- **Logic**: Check CEST is valid for given NCM per Convênio ICMS 142/2018
- **Cache TTL**: 3600s (1 hour)

### 5. NFE_VALOR_TOTAL (HIGH)
- **Description**: Validate total NF-e value matches sum of items + taxes + freight
- **Logic**: Sum vProd + vFrete + vSeg + vDesc + vII + vIPI + vPIS + vCOFINS + vICMS + vST + vFCP ≈ vNF
- **Cache TTL**: 3600s (1 hour)

### 6. NFE_TRANSPORTADORA (HIGH)
- **Description**: Validate carrier (transportadora) data on NF-e
- **Logic**: Check CNPJ/CPF, IE, UF, placa veículo, RNTRC when modal = rodoviário
- **Cache TTL**: 3600s (1 hour)

### 7. NFE_DESTINATARIO (HIGH)
- **Description**: Validate recipient (destinatário) data on NF-e
- **Logic**: Check CNPJ/CPF, IE (if contributor), endereço completo, UF match
- **Cache TTL**: 3600s (1 hour)

## Acceptance Criteria

### Implementation
- [ ] Create 7 rule classes in `backend/app/services/rules_critical.py`
- [ ] Register rules in `_load_builtin_rules()` in `rules_engine_v2.py`
- [ ] Each rule extends `BaseRule` with proper `evaluate()` method
- [ ] Return `DiscrepancyResult` with correct rule_code, rule_name, discrepancy_type

### Testing
- [ ] Unit tests for each rule (triggered/not triggered/edge cases)
- [ ] Integration tests with RulesEngineV2
- [ ] Cache behavior tests (TTL 3600s)
- [ ] All existing + Card #34 tests still pass

### Quality Gates
- [ ] `python -m pytest tests/test_rules_critical.py -v` passes
- [ ] `python -m pytest tests/test_rules_critical.py::TestNFEHighRules -v` passes (new tests)
- [ ] `python -m ruff check .` no new errors
- [ ] `python -m mypy .` passes

## Technical Details

### Files to Modify
1. `backend/app/services/rules_critical.py` - Add 7 new rule classes
2. `backend/app/services/rules_engine_v2.py` - Register in `_load_builtin_rules()`
3. `backend/tests/test_rules_critical.py` - Add test class `TestNFEHighRules`

### Rule Template
```python
class NFEFCPRule(BaseRule):
    rule_code = RuleCode.NFE_FCP
    rule_name = "Validação FCP NF-e"
    tags = {"nfe", "fcp", "high"}
    cache_ttl = 3600

    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        # Implementation here
        pass
```

## References
- RuleCode enum: `backend/app/services/rules_engine_v2.py:43-50`
- Existing rules pattern: `backend/app/services/rules_critical.py`
- Test patterns: `backend/tests/test_rules_critical.py`

## Dependencies
- Card #34: NF-e Critical Rules (must be done first)

## Definition of Done
- [ ] 7 rule classes implemented and registered
- [ ] Unit tests for all 7 rules (≥3 tests each = 21 new tests)
- [ ] All 70 tests pass (49 existing + 21 new)
- [ ] Card moved to `review/`