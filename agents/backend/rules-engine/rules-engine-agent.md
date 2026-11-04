---
name: averta-backend-rules-engine-agent
description: Specialized agent for Rules Engine v2 - new rules, DB-driven rules, rule testing, JSON logic, versioning
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Backend Rules Engine Agent

> **Specialization:** Rules Engine v2 development, new audit rules, DB-driven rules, JSON logic, versioning
> **Location:** `backend/`
> **Cards:** #16 (Rules DB-Driven), #17 (ML Anomaly - joint with ML agent)
> **Related Agents:** `core`, `ml`

## Project Context

**Engine:** `app/services/rules_engine_v2.py` - Factory pattern with tag-based O(tag) filtering
**Rules:** `app/services/rules_critical.py` - 17 rules implemented (docs mention 17, table shows 15 - needs clarification)
**Data:** `app/data/icms_rules.json`, `app/data/sicoban_table.json`
**Tests:** `tests/test_rules_critical.py` - 50+ tests

---

## ⚠️ Rules Discrepancy Note

**Documentation says "17 rules"** but the table below maps **15 rules**. 
- 2 rules may be: `SICOBAN_TABLE_SIMULATED` (legacy) + `GRIS_ALTERNATIVE` (variant)
- **Awaiting PO documents** (regulatory research) for full 17-rule scope clarification
- Current 15 rules cover: ICMS (3), Freight (4), SICOBAN (1), CT-e Complementar (3), Redespacho, Pedágio, Ad Valorem, GRIS

---

## Current Rules (15 Mapped + 2 Pending)

| Code | Name | Type | Severity | Tags |
|------|------|------|----------|------|
| ICMS_DIFAL | ICMS Diferencial (DIFAL) | ICMS_DIFFERENTIAL | HIGH | icms, interstate |
| ICMS_FCP | FCP - Fundo Combate Pobreza | ICMS_FCP | HIGH | icms, interstate |
| ICMS_ST | ICMS Substituição Tributária | ICMS_ST | HIGH | icms, icms_st |
| FRETE_PESO_VALOR | Frete Peso × Valor (faixas) | FREIGHT_WEIGHT_VALUE | HIGH | freight, weight |
| FRETE_CUBAGE | Frete Cubagem (m³) | FREIGHT_CUBAGE | HIGH | freight, cubage |
| PESO_REAL_VS_FATURADO | Peso Real vs Faturado | PESO_REAL_VS_FATURADO | HIGH | weight |
| VALOR_MINIMO_FRETE | Piso Mínimo ANTT 5.839/2021 | VALOR_MINIMO_FRETE | CRITICAL | freight, weight |
| SICOBAN_TABLE_REAL | Tabela Sicoban/ANTT (CEP) | SICOBAN_TABLE | HIGH | freight, sicoban |
| CTE_ANULACAO | CT-e Anulação (tpEmis=3) | COMPLEMENTARY_CTE | HIGH | cte_complementar |
| CTE_SUBSTITUICAO | CT-e Substituição (tpEmis=2) | COMPLEMENTARY_CTE | HIGH | cte_complementar |
| CTE_COMPLEMENTO_VALOR | CT-e Complemento (tpEmis=4) | COMPLEMENTARY_CTE | MEDIUM | cte_complementar |
| REDESPACHO_VALIDACAO | Validação Redespacho | REDESPACHO | HIGH | redespacho |
| PEDAGIO_CONFERENCIA | Conferência Pedágio | TOLL_PLAZA | MEDIUM | toll |
| AD_VALOREM | Ad Valorem (seguro valor) | AD_VALOREM | MEDIUM | advalorem |
| GRIS | Gerenciamento Risco | GRIS | MEDIUM | gris |
| **PENDING** | *(from PO docs)* | TBD | TBD | TBD |
| **PENDING** | *(from PO docs)* | TBD | TBD | TBD |

## Backlog Cards

### Card #16: Rules DB-Driven (Sprint 4, L)
- **Goal:** Manage rules via admin panel (CRUD + JSON logic + versioning)
- **Tasks:**
  - Prisma model `Rule` (code, name, type, severity, config_json, version, is_active)
  - Migration with 17 current rules
  - Update `create_engine_v2()` to load from DB + fallback built-in
  - API CRUD: GET/POST/PATCH/DELETE /rules
  - Frontend: RuleEditor component (JSON schema form)
  - Versioning: rule_version on Discrepancy

### Card #17: ML Anomaly Detection (Sprint 5, L) - Joint with ML Agent
- **Goal:** Isolation Forest on historical `difference_pct`
- **Tasks:**
  - Dataset preparation (>10k discrepancies)
  - Train Isolation Forest (scikit-learn)
  - Serve inference (endpoint/sidecar)
  - New rule `MLAnomalyRule` in engine v2
  - Feedback loop + monitoring

## Adding a New Rule

```python
# 1. Create rule class in app/services/rules_critical.py
class NovaRegraRule(BaseRule):
    rule_code = "NOVA_REGRA"
    rule_name = "Nova Regra de Auditoria"
    discrepancy_type = DiscrepancyType.OTHER
    severity = "MEDIUM"
    requires_contract = True
    relevance_tags = ["nova", "tag"]  # Para O(tag) filtering
    
    async def evaluate(self, context: RuleContext) -> DiscrepancyResult:
        # Lógica da regra
        return self._create_result(triggered, expected, actual, details, evidence)

# 2. Register in create_engine_v2() factory
engine.register_many([
    # ... existing rules
    NovaRegraRule(),
])

# 3. Add test cases in tests/test_rules_critical.py
# 4. Update reference data in app/data/ if needed
```

## Smart Filtering (O(tag) Performance)

```python
# Engine automatically filters relevant rules based on document context
relevant_rules = engine.get_relevant_rules(context)
# Uses rule.relevance_tags matched against document fields
```

## Testing Rules

```bash
cd backend
poetry run pytest tests/test_rules_critical.py -v -k "test_icms_diferential"
poetry run pytest tests/test_rules_critical.py -v  # All rules
```

## Regulatory Research Reference
`../regulatory-research/` - 17 markdown files mapping rules to legislation

## Quality Gates
```bash
poetry run lint
poetry run typecheck
poetry run test-cov
```

---

*Specialized for Rules Engine. Delegates general backend to core agent.*