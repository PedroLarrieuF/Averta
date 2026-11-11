---
id: 21
title: "Reports Page - PDF/Excel Export + Scheduling"
priority: high
type: feature
agent: frontend
sprint: 2
estimate: L
status: done
created: 2026-11-03
reviewed_by: techlead
---

# Card #21: Reports Page - PDF/Excel Export + Scheduling

## Description
Replace the `ComingSoon` placeholder in `frontend/src/pages/Reports.tsx` with a complete Reports page implementation featuring dashboard KPIs, PDF export, Excel export, and report scheduling.

## Acceptance Criteria

### Dashboard View
- [ ] KPI cards showing: Total Recovered, Success Fee, Net Recovery, Discrepancy Count, Top Carrier, Top Rule
- [ ] Time series chart (Recharts) showing recovery over time (last 12 months)
- [ ] Top 5 carriers by recovery amount (bar chart)
- [ ] Top 5 rules by discrepancy count (bar chart)
- [ ] Date range selector (last 7d, 30d, 90d, 12m, custom)

### PDF Export
- [ ] "Export PDF" button triggers `GET /api/v1/reports/pdf?start_date&end_date`
- [ ] Loading state during generation
- [ ] PDF downloads with filename `averta-report-{date}.pdf`
- [ ] PDF includes: header, KPIs, charts as images, tables

### Excel Export
- [ ] "Export Excel" button triggers `GET /api/v1/reports/excel?start_date&end_date`
- [ ] Multi-sheet workbook: Dashboard, Discrepancies, Contests, Payments
- [ ] Excel downloads with filename `averta-report-{date}.xlsx`

### Report Scheduling
- [ ] "Schedule Report" button opens modal
- [ ] Form: frequency (weekly/monthly), day/time, recipients (email list), format (PDF/Excel)
- [ ] POST to `POST /api/v1/reports/schedule`
- [ ] List scheduled reports with edit/delete actions

## Technical Requirements

### API Endpoints
```typescript
// Already available in backend
GET /api/v1/reports/dashboard?start_date&end_date
GET /api/v1/reports/pdf?start_date&end_date
GET /api/v1/reports/excel?start_date&end_date
POST /api/v1/reports/schedule
GET /api/v1/reports/scheduled
PATCH /api/v1/reports/scheduled/{id}
DELETE /api/v1/reports/scheduled/{id}
```

### Components to Create
- `src/components/reports/ReportsDashboard.tsx` - Main dashboard with KPIs + charts
- `src/components/reports/ReportCharts.tsx` - Recharts wrapper components
- `src/components/reports/ExportButtons.tsx` - PDF/Excel export buttons
- `src/components/reports/ScheduleModal.tsx` - Schedule configuration modal
- `src/components/reports/ScheduledReportsList.tsx` - List of scheduled reports

### Hooks to Create (delegate to state-agent)
- `useReportsDashboard(startDate, endDate)` - TanStack Query for dashboard data
- `useExportReport(format, startDate, endDate)` - Mutation for PDF/Excel export
- `useScheduledReports()` - List scheduled reports
- `useScheduleReport()` - Create/update/delete scheduled reports

### Types Needed (delegate to state-agent)
```typescript
interface ReportsDashboardResponse {
  kpis: {
    total_recovered: number;
    success_fee: number;
    net_recovery: number;
    discrepancy_count: number;
    top_carrier: { name: string; amount: number };
    top_rule: { code: string; count: number };
  };
  time_series: { date: string; recovered: number }[];
  top_carriers: { carrier: string; amount: number }[];
  top_rules: { rule: string; count: number }[];
}

interface ScheduledReport {
  id: string;
  frequency: 'weekly' | 'monthly';
  day_of_week: number; // 0-6
  time: string; // HH:mm
  recipients: string[];
  format: 'pdf' | 'excel';
  is_active: boolean;
  created_at: string;
}
```

## Dependencies
- Card #01: Testing infrastructure (DONE)
- Backend: Reports endpoints already implemented

## Design References
- `frontend/src/index.css` - KPI cards: `.kpi-card`, `.kpi-value`, `.kpi-label`, `.kpi-trend`
- `frontend/src/components/` - Use existing Table, Modal, Button, Badge
- Recharts for charts (already in package.json)

## Testing Requirements
- Unit tests for each component
- Integration test for export flows
- MSW handlers for all report endpoints
- Accessibility tests (jest-axe)

## Definition of Done
- [ ] Page renders without errors
- [ ] Dashboard shows real data from API
- [ ] PDF export works and downloads valid PDF
- [ ] Excel export works and downloads valid XLSX
- [ ] Scheduling CRUD works
- [ ] All quality gates pass: `pnpm lint && pnpm build && pnpm test`
- [ ] Tests written and passing
- [ ] Card moved to `review/`

## Notes
- Backend reports endpoints are already implemented per `backend/README.md`
- Use `formatCurrency` from `utils/helpers.ts` for BRL formatting
- Date handling: UTC from API, local display via `formatDate`/`formatDateTime`
- Loading states: use existing `.btn-loading` or Skeleton components