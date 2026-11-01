---
id: 06
title: "Decision: Deprecate NestJS Backend (packages/backend)"
priority: high
type: decision
agent: techlead
sprint: 1
estimate: S
status: ready
created: 2026-11-01
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
- [ ] Documentar decisão em ADR (`docs/adr/001-primary-backend.md`)
- [ ] Arquivar `packages/backend/` (mover para `archived/` ou deletar)
- [ ] Atualizar `package.json` root - remover `@averta/backend` workspace se não usado
- [ ] Atualizar `turbo.json` - remover pipeline do backend NestJS
- [ ] Comunicar ao time no `#averta-tech`
- [ ] Atualizar documentação onboarding

## Acceptance Criteria
- [ ] ADR criado e aprovado
- [ ] `packages/backend/` removido ou arquivado
- [ ] Monorepo limpo (apenas frontend + shared types se houver)
- [ ] Time alinhado

## Referências
- `TECHLEAD_REVIEW.md` - TD-008, Decisions Needed
- `backend/README.md` - Source of truth
- `packages/backend/package.json` - NestJS implementation