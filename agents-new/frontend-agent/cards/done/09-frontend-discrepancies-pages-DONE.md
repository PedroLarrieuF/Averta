---
id: 09
title: "Build Discrepancies List & Review Page"
priority: critical
type: feature
agent: frontend
sprint: 2
estimate: L
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 09: Build Discrepancies List & Review Page

## Contexto
Página principal de trabalho do auditor. Lista divergências, permite revisar, selecionar para contestação.

## Definition of Ready
- [x] API: GET /discrepancies, GET /discrepancies/summary, PATCH /discrepancies/bulk-status, POST /discrepancies/{id}/review
- [x] Helpers: getStatusBadge, getSeverityBadge, formatCurrency
- [x] Design system + Document pages (Card 08) - dependency

## Tasks
- [ ] `src/pages/DiscrepanciesPage.tsx` - lista principal com sidebar de filtros
- [ ] `src/pages/DiscrepancyDetailPage.tsx` - detalhe com evidências, expected/actual
- [ ] Hooks:
  - `src/hooks/useDiscrepancies.ts` - list, summary, bulk, review
  - `src/hooks/useDiscrepancyActions.ts` - bulk status, review
- [ ] Componentes:
  - `src/components/discrepancies/DiscrepancyTable.tsx` - colunas: rule, severity, status, values, diff, actions
  - `src/components/discrepancies/DiscrepancyFilters.tsx` - status, severity, rule, carrier, date range
  - `src/components/discrepancies/DiscrepancySummaryCards.tsx` - KPIs por status/severity/rule
  - `src/components/discrepancies/DiscrepancyDetailModal.tsx` - evidence, details, actions
  - `src/components/discrepancies/BulkActionBar.tsx` - selecionar múltiplas → revisar/contestar
- [ ] Fluxo:
  - Lista com filtros persistidos (URL query params)
  - Seleção múltipla (checkbox) → bulk actions
  - Click row → modal detalhe
  - "Revisar" → PATCH status → toast success
  - "Contestar selecionadas" → navega para ContestCreatePage
- [ ] Testes: list, filters, bulk actions, detail modal

## API Contract
```typescript
// GET /discrepancies?status=OPEN&severity=HIGH&rule_code=ICMS_DIFAL
// GET /discrepancies/summary → { by_status: {...}, by_severity: {...}, by_rule: {...} }
// PATCH /discrepancies/bulk-status { ids: string[], status: 'IN_REVIEW' }
// POST /discrepancies/{id}/review { notes: string }
```

## Acceptance Criteria
- [ ] Lista carrega < 1s (paginada)
- [ ] Filtros combinados funcionam
- [ ] Resumo KPIs atualiza com filtros
- [ ] Seleção múltipla + bulk actions
- [ ] Modal detalhe mostra evidence, expected vs actual
- [ ] Status badge cores corretas (helpers)
- [ ] Testes integração

## Referências
- `backend/README.md` - seção "Discrepancies"
- `frontend/utils/helpers.ts` - getStatusBadge, getSeverityBadge