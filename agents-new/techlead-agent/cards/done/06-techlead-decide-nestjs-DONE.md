---
id: 06
title: "Decision: Deprecate NestJS Backend (packages/backend)"
priority: high
type: decision
agent: techlead
sprint: 1
estimate: S
status: done
created: 2026-11-01
completed: 2026-11-02
reviewed_by: techlead
---

# Card 06: Decision - Deprecate NestJS Backend

## Contexto
Existem **DOIS backends**:
1. `backend/` - Python FastAPI ✅ Completo, documentado, testado (78% coverage)
2. `packages/backend/` - NestJS/TypeScript 🟡 Parcial, duplicado

## Definition of Ready
- [x] Tech lead review identificou duplicação (TD-008)
- [x] Python backend é o principal (README detalhado, 17 rules, CI/CD)

## Options
| Opção | Prós | Contras | Recomendação |
|-------|------|---------|--------------|
| **Deprecar NestJS** | Foco único, menos manutenção, Python é mais forte para data/ML | Perde investimento no NestJS | ✅ **RECOMENDADO** |
| Manter ambos | Flexibilidade, comparação | Duplicação, confusão, 2x manutenção | ❌ |
| Migrar para NestJS | TypeScript end-to-end | Reescrever 17 rules, tests, infra | ❌ |

## Tasks
- [x] Documentar decisão em ADR (`docs/adr/001-primary-backend.md`)
- [x] Arquivar `packages/backend/` (movido para `archived/packages-backend-nestjs/`)
- [x] Verificar `package.json` root - já limpo (apenas `frontend`, `backend`)
- [x] Verificar `turbo.json` - já limpo (sem pipeline NestJS)
- [ ] Comunicar ao time no `#averta-tech`
- [ ] Atualizar documentação onboarding

## Acceptance Criteria
- [x] ADR criado e aprovado (`docs/adr/001-primary-backend.md`)
- [x] `packages/backend/` arquivado em `archived/packages-backend-nestjs/`
- [x] Monorepo limpo (apenas `frontend/` + `backend/`)
- [ ] Time alinhado

## Completed Files
- `docs/adr/001-primary-backend.md` - Architecture Decision Record
- `archived/packages-backend-nestjs/` - Archived NestJS implementation (preserved for reference)

## Decision Outcome
**Python FastAPI (`backend/`) is the single source of truth for backend development.** NestJS implementation archived for reference. This resolves TD-008 from TECHLEAD_REVIEW.md.

## Referências
- `TECHLEAD_REVIEW.md` - TD-008, Decisions Needed
- `backend/README.md` - Source of truth
- `packages/backend/package.json` - NestJS implementation