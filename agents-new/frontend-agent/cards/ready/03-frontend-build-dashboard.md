---
id: 03
title: "Build Dashboard with KPIs (Recharts)"
priority: critical
type: feature
agent: frontend
sprint: 1
estimate: L
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 03: Build Dashboard with KPIs

## Contexto
Página principal pós-login. Consome `GET /api/v1/reports/dashboard`.

## Definition of Ready
- [x] API endpoint documentado no backend README
- [x] Design system tem KPICard, grid-kpi classes
- [x] Recharts instalado

## Tasks
- [ ] Criar `src/pages/DashboardPage.tsx`
- [ ] Criar hook `src/hooks/useDashboard.ts` com TanStack Query
- [ ] Criar componentes:
  - `src/components/dashboard/KPICard.tsx` (usa .kpi-card, .kpi-value, .kpi-trend)
  - `src/components/dashboard/TopCarriersChart.tsx` (BarChart Recharts)
  - `src/components/dashboard/TopRulesChart.tsx` (PieChart Recharts)
  - `src/components/dashboard/TimeSeriesChart.tsx` (LineChart Recharts)
- [ ] Layout responsivo (grid-kpi: 1 col mobile, 2 tablet, 4 desktop)
- [ ] Loading skeletons para cards
- [ ] Error state com retry
- [ ] Filtro de período (últimos 7/30/90 dias)
- [ ] Testes: hook, componentes, página

## API Contract (GET /reports/dashboard)
```typescript
interface DashboardResponse {
  kpis: {
    total_documents: number
    total_discrepancies: number
    total_recovered: number
    pending_contests: number
    success_rate: number
  }
  top_carriers: Array<{ carrier_name: string; count: number; value: number }>
  top_rules: Array<{ rule_code: string; count: number; total_difference: number }>
  time_series: Array<{ date: string; discrepancies: number; recovered: number }>
}
```

## Acceptance Criteria
- [ ] Dashboard carrega em < 2s
- [ ] KPIs exibidos corretamente com formatação BRL
- [ ] Gráficos interativos (tooltip, legend)
- [ ] Filtro de período atualiza dados
- [ ] Empty state se sem dados
- [ ] Testes de integração com MSW

## Referências
- `frontend-agent.md` - helpers.formatCurrency, Recharts
- `backend/README.md` - seção "Relatórios & Export"