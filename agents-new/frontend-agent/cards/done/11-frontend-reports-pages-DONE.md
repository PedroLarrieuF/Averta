---
id: 11
title: "Build Reports Pages (Dashboard, PDF Export, Excel Export, Scheduling)"
priority: high
type: feature
agent: frontend
sprint: 3
estimate: L
status: done
created: 2026-11-01
reviewed_by: techlead
---

# Card 11: Build Reports Pages

## Contexto
Páginas de relatórios e dashboards para visualização de KPIs, exportação de dados e agendamento de relatórios automáticos.

## Definition of Ready
- [x] API: GET /reports/dashboard, GET /reports/pdf, GET /reports/excel, POST /reports/schedule
- [x] Design system components (Card 07) - KPICard, Table, Button, Select, DatePicker
- [x] Recharts instalado para gráficos
- [x] Auth + role checks (ADMIN, MANAGER, AUDITOR)

## Tasks
### Pages
- [ ] `src/pages/ReportsPage.tsx` - Layout principal com abas: Dashboard, Exportar, Agendar
- [ ] `src/pages/ReportDashboardPage.tsx` - KPIs + gráficos (Recharts)
- [ ] `src/pages/ReportExportPage.tsx` - PDF/Excel export com filtros
- [ ] `src/pages/ReportSchedulePage.tsx` - CRUD de agendamentos semanais

### Hooks
- [ ] `src/hooks/useReports.ts` - dashboard, pdf, excel, schedule CRUD
- [ ] `src/hooks/useReportDashboard.ts` - KPIs, time series, top carriers, top rules

### Components
- [ ] `src/components/reports/ReportDashboard.tsx` - Grid de KPICards + gráficos
- [ ] `src/components/reports/KPIChart.tsx` - Recharts wrapper (LineChart, BarChart, PieChart)
- [ ] `src/components/reports/ReportFilters.tsx` - Período, carrier, cliente, status, regra
- [ ] `src/components/reports/ExportPanel.tsx` - Formato (PDF/Excel), filtros, botão download
- [ ] `src/components/reports/ScheduleForm.tsx` - Frequência, dia/hora, destinatários, formato
- [ ] `src/components/reports/ScheduleList.tsx` - Lista agendamentos com ações (editar, pausar, deletar)

### Gráficos (Recharts)
- [ ] **KPIs Cards**: Total discrepâncias, Valor recuperado, Taxa sucesso, Top 3 carriers
- [ ] **Time Series**: Discrepâncias por mês (LineChart)
- [ ] **Top Carriers**: BarChart horizontal - valor recuperado por carrier
- [ ] **Top Rules**: PieChart - distribuição por tipo de regra
- [ ] **Severity Distribution**: Stacked bar - severidade por mês

### Export
- [ ] **PDF**: ReportLab backend → blob → download/preview
- [ ] **Excel**: OpenPyXL backend → multi-sheet (Resumo, Detalhes, Gráficos)
- [ ] Filtros aplicados no export devem coincidir com tela

### Agendamento
- [ ] Frequência: Semanal (dia da semana + hora)
- [ ] Destinatários: lista emails (usuários da company + extras)
- [ ] Formato: PDF ou Excel
- [ ] Filtros: salvos no agendamento
- [ ] Status: Ativo/Pausado
- [ ] Preview antes de salvar

### Testes
- [ ] Dashboard carrega KPIs e gráficos < 2s
- [ ] Filtros atualizam gráficos em tempo real
- [ ] Export PDF/Excel gera arquivos válidos
- [ ] Agendamento CRUD funcional
- [ ] Testes acessibilidade gráficos (aria-labels, keyboard nav)

## API Contract
```typescript
// GET /reports/dashboard?period=30d&carrier_id=xxx
interface DashboardResponse {
  kpis: { total_discrepancies: number; total_recovered: number; success_rate: number; avg_resolution_days: number }
  time_series: { date: string; count: number; value: number }[]
  top_carriers: { carrier_id: string; carrier_name: string; recovered: number; count: number }[]
  top_rules: { rule_code: string; count: number; total_value: number }[]
  by_severity: { severity: string; count: number }[]
}

// GET /reports/pdf?period=30d&format=pdf
// GET /reports/excel?period=30d&format=excel

// POST /reports/schedule
interface ScheduleRequest {
  name: string;
  frequency: 'weekly';
  day_of_week: number; // 0-6
  hour: number; // 0-23
  format: 'pdf' | 'excel';
  filters: ReportFilters;
  recipients: string[]; // emails
}
```

## Acceptance Criteria
- [ ] Dashboard renderiza KPIs + 4 gráficos
- [ ] Filtros funcionam e persistem na URL
- [ ] PDF download abre corretamente
- [ ] Excel download tem múltiplas abas
- [ ] Agendamento criado → job no Celery Beat
- [ ] Email enviado com anexo no horário agendado
- [ ] Testes integração completa

## Referências
- `backend/README.md` - seção "Reports"
- `frontend/src/utils/helpers.ts` - formatCurrency, formatDate
- Recharts: https://recharts.org/
- `frontend/src/components/ui/KPICard.tsx` - componente base