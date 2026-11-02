---
id: 16
title: "Rules DB-Driven (CRUD no painel + JSON logic + versionamento)"
priority: medium
type: feature
agent: backend
sprint: 4
estimate: L
status: done
created: 2026-11-01
completed: 2026-11-02
reviewed_by: techlead
---

# Card 16: Rules DB-Driven

## Contexto
Roadmap médio prazo. Atualmente 17 rules hardcoded. Objetivo: gerenciar rules via painel admin.

## Definition of Ready
- [ ] Decision: schema para rule definition (JSON logic)
- [ ] UI para rule editor no frontend (Settings)
- [ ] Engine v2 já suporta factory pattern

## Tasks
- [ ] Adicionar model `Rule` no Prisma (code, name, type, severity, config_json, version, is_active)
- [ ] Migration para popular com 17 rules atuais
- [ ] Atualizar `create_engine_v2()` para carregar do DB + fallback built-in
- [ ] API CRUD: GET/POST/PATCH/DELETE /rules
- [ ] Frontend: RuleEditor component (JSON schema form)
- [ ] Versionamento: rule_version no Discrepancy
- [ ] Testes: engine com rules DB, fallback, versioning

## Rule Config JSON Schema (proposta)
```json
{
  "rule_code": "ICMS_DIFAL",
  "version": 1,
  "config": {
    "enabled": true,
    "parameters": {
      "min_difference": 0.01
    },
    "conditions": [
      {"field": "uf_origem", "operator": "!=", "value": "uf_destino"}
    ]
  }
}
```

## Acceptance Criteria
- [ ] Rules gerenciáveis via API/UI sem deploy
- [ ] Versionamento rastreável por discrepância
- [ ] Fallback para built-in se DB falhar
- [ ] Performance similar (cache Redis)

## Referências
- `TECHLEAD_REVIEW.md` - Roadmap médio prazo
- `backend/app/services/rules_engine_v2.py` - factory pattern