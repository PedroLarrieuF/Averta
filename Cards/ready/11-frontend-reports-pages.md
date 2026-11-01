---
id: 11
title: "Build Reports Pages (Dashboard, PDF Export, Excel Export, Scheduling)"
priority: high
type: feature
agent: frontend
sprint: 3
estimate: L
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 11: Build Reports Pages

## Contexto
Relatórios gerenciais: dashboard KPIs (já no Card 03), export PDF/Excel, agendamento semanal.

## Definition of Ready
- [x] API: GET /reports/dashboard, GET /reports/pdf, GET /reports/excel, POST /reports/schedule
- [x] Dashboard page (Card 03) - base
- [x] Recharts para gráficos

## Tasks
- [ ] `src/pages/ReportsPage.tsx` - aba Dashboard (reutiliza Card 03) + aba Export
- [ ] `src/components/reports/ExportPanel.tsx` - filtros + botões PDF/Excel
- [ ] `src/components/reports/ScheduleForm.tsx` - configurar relatório semanal
- [ ] `src/components/reports/ReportPreview.tsx` - preview antes de exportar
- [ ] Hooks:
  - `src/hooks/useReports.ts` - dashboard, pdf, excel, schedule
- [ ] Export Flow:
  - Selecionar período, filtros
  - "Gerar PDF" → GET /reports/pdf?... → blob → download
  - "Gerar Excel" → GET /reports/excel?... → blob → download
  - Progress indicator para relatórios grandes
- [ ] Scheduling:
  - Form: dia da semana, hora, destinatários, filtros padrão
  - POST /reports/schedule → confirmação
  - Lista agendamentos ativos
- [ ] Testes: export, scheduling, preview

## API Contract
```typescript
// GET /reports/pdf?date_from=2024-01-01&date_to=2024-01-31&carrier_id=1
// Returns: application/pdf

// GET /reports/excel?... 
// Returns: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

// POST /reports/schedule
interface ScheduleRequest {
  frequency: 'weekly'
  day_of_week: 1-7
  hour: 0-23
  recipients: string[] // emails
  filters: ReportFilters
}
```

## Acceptance Criteria
- [ ] PDF export abre corretamente (ReportLab)
- [ ] Excel export múltiplas abas (Discrepancies, Contests, KPIs)
- [ ] Filtros aplicados no export
- [ ] Agendamento salva e envia email semanal
- [ ] Loading states durante geração
- [ ] Testes integração

## Referências
- `backend/README.md` - seção "Relatórios & Export"
- `frontend/utils/helpers.ts` - formatCurrency, formatDate