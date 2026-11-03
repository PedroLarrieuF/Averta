---
name: averta-frontend-agent
description: Dedicated 100% Frontend Agent for AvertaSaaS - React + Vite + TypeScript + Tailwind + Radix UI. Owns all frontend Kanban cards.
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents, Agent
---

# AvertaSaaS Frontend Agent (Dedicated v2.4 - 6/12 Pages Complete)

> **Location:** `frontend/` (moved from `packages/frontend/` on 2026-11-01)
> **Mission:** Complete the frontend for freight audit SaaS - replace all placeholder pages with full implementations
> **Standard:** After each card completion, update this agent + move card to `review/`
> **Last Updated:** 2026-11-03 (Card #11 Reports Page completed)

---

## 🎯 ACTUAL Current State (2026-11-03)

### ✅ Already Built (DO NOT REBUILD)
| Area | Status | Files |
|------|--------|-------|
| **Routing & Layouts** | ✅ COMPLETE | `App.tsx`, `MainLayout`, `AuthLayout`, Protected/Public routes |
| **Auth Pages** | ✅ COMPLETE | `Login.tsx`, `Register.tsx` (with forms, validation) |
| **Dashboard** | ✅ COMPLETE | `Dashboard.tsx` (KPI cards, charts placeholder) |
| **Documents Page** | ✅ COMPLETE (Card #08) | `Documents.tsx` + `DocumentsTable`, `UploadZone`, `DocumentDetailModal` |
| **Discrepancies Page** | ✅ COMPLETE (Card #09) | `DiscrepanciesPage.tsx` + 5 components (Table, Filters, DetailModal, SummaryCards, BulkActionBar) |
| **Contests Page** | ✅ COMPLETE (Card #10) | `ContestsPage.tsx`, `ContestCreatePage.tsx`, `ContestDetailPage.tsx`, `ContestNegotiatePage.tsx` + 8 components (Table, CreateStepper, Timeline, ItemTable, CommunicationThread, PaymentForm, SuccessFeeCalculator, PDFViewer) |
| **Reports Page** | ✅ COMPLETE (Card #11) | `ReportsPage.tsx`, `ReportExportPage.tsx` + 7 components (Dashboard, Filters, KPIChart, ExportPanel, ScheduleForm, ScheduleList) + Tabs, Select, Switch, KPICard design system components |
| **Design System Components** | ✅ COMPLETE | `Button`, `Input`, `Card`, `Badge`, `Table`, `Modal`, `DropdownMenu`, `Avatar`, `Tabs`, `Select`, `Switch`, `KPICard` (Tabs, Select, Switch, KPICard added in Card #11) |
| **Auth System** | ✅ COMPLETE | `auth-context.tsx`, `auth-storage.ts`, `useAuth()` hook |
| **API Client** | ✅ COMPLETE | `api.ts` (axios + interceptors + token refresh) |
| **Utilities** | ✅ COMPLETE | `helpers.ts` (formatters, roles, badges, cn) |
| **Hooks** | ✅ PARTIAL | `useApi.ts` (TanStack Query wrapper), `useDiscrepancyActions.ts` |
| **Testing Infrastructure** | ✅ COMPLETE (Card #01) | Vitest + RTL + MSW + jest-axe + @faker-js/faker (72 tests passing) |

### 🔴 NEEDS IMPLEMENTATION (Replace Placeholders)
| Page | Card | Priority | Current State |
|------|------|----------|---------------|
| **Settings** | #15 | 🟡 HIGH | `ComingSoon` - needs Company, Users, Carriers, Contracts, Notifications |
| **Clients** | #22 | 🟡 HIGH | `ComingSoon` - needs CRUD |
| **Carriers** | #23 | 🟡 HIGH | `ComingSoon` - needs CRUD |
| **Contracts** | #24 | 🟡 HIGH | `ComingSoon` - needs CRUD + FreightTable editor |
| **Profile** | #25 | 🟢 MEDIUM | `ComingSoon` - needs profile management |

### 🟡 NEEDS ENHANCEMENT
| Area | Card | Current State |
|------|------|---------------|
| **Dashboard Charts** | #03 | Placeholder - needs Recharts implementation |
| **Design System** | #07 | Components exist but need: Tooltip, Toast, Pagination, EmptyState (Tabs, Select, Switch, KPICard ✅ done in Card #11) |
| **Bundle Optimization** | #26 | 995kB main chunk - needs code splitting / lazy routes |
| **TypeScript Types** | #27 | Missing barrel exports in `frontend/src/types/index.ts` |

---

## 📋 Kanban Board (Local to This Agent)

**Location:** `agents-new/frontend-agent/cards/`

```
agents-new/frontend-agent/cards/
├── backlog/       # Future work, not yet prioritized
├── ready/         # Prioritized, ready to start
├── in-progress/   # Currently being worked on
├── review/        # Completed, awaiting review
└── done/          # Completed and accepted
```

### Current Sprint Cards

| Card | Title | Status | Priority | Estimate |
|------|-------|--------|----------|----------|
| #01 | QA Setup: Vitest + RTL + MSW | ✅ **Done** | CRITICAL | M |
| #03 | Build Dashboard with Charts | 🔴 Ready | HIGH | M |
| #07 | Build Design System Components | 🔴 Ready | HIGH | L |
| #10 | Contests Page (create/detail/negotiate/pay) | ✅ **Done** | CRITICAL | XL |
| #11 | Reports Page (PDF/Excel export, scheduling) | ✅ **Done** | HIGH | L |
| #15 | Settings Pages (Company/Users/Carriers/Contracts/Notifications) | 🔴 Ready | HIGH | M |
| #21 | Reports Page (NEW - detailed spec) | ✅ **Done** (merged into #11) | HIGH | L |
| #22 | Clients Page (CRUD) | 🔴 Ready | HIGH | M |
| #23 | Carriers Page (CRUD) | 🔴 Ready | HIGH | M |
| #24 | Contracts Page (CRUD + FreightTable editor) | 🔴 Ready | HIGH | L |
| #25 | Profile Page (user profile management) | 🔴 Ready | MEDIUM | S |
| #26 | Code Splitting & Bundle Optimization | 🔴 Ready | MEDIUM | M |
| #27 | TypeScript Types Barrel Exports | 🔴 Ready | LOW | S |

### Card Lifecycle (This Agent Owns)
1. **Tech Lead assigns** → Card moved to `ready/`
2. **Agent picks up** → Move to `in-progress/`, start implementation
3. **Implementation complete** → Move to `review/`, notify Tech Lead
4. **Tech Lead approves** → Move to `done/`, update this agent.md

---

## 📁 Project Structure (Actual - 2026-11-03)

```
frontend/
├── src/
│   ├── main.tsx                    # QueryClient, AuthProvider, BrowserRouter
│   ├── App.tsx                     # Routes + Protected/Public wrappers ✅
│   ├── index.css                   # Design system (Tailwind + CSS vars) ✅
│   ├── services/
│   │   └── api.ts                  # Axios + interceptors + token refresh ✅
│   ├── store/
│   │   ├── auth-context.tsx        # React Context + useAuth() ✅
│   │   └── auth-storage.ts         # localStorage tokens ✅
│   ├── utils/
│   │   └── helpers.ts              # Formatters, roles, badges ✅
│   ├── components/                 # Design system ✅
│   │   ├── index.ts                # Barrel exports
│   │   ├── Button.tsx              # variants: primary/secondary/ghost/danger
│   │   ├── Input.tsx               # label, error, disabled
│   │   ├── Card.tsx                # header, body, footer
│   │   ├── Badge.tsx               # variants: success/warning/danger/primary/secondary
│   │   ├── Table.tsx               # sortable, pagination ready
│   │   ├── Modal.tsx               # Dialog + AlertDialog (Radix)
│   │   ├── DropdownMenu.tsx        # Radix DropdownMenu
│   │   ├── Avatar.tsx              # Radix Avatar
│   │   ├── discrepancies/          # Feature components (Card #09) ✅
│   │   │   ├── DiscrepanciesTable.tsx
│   │   │   ├── DiscrepancyFilters.tsx
│   │   │   ├── DiscrepancyDetailModal.tsx
│   │   │   ├── DiscrepancySummaryCards.tsx
│   │   │   └── BulkActionBar.tsx
│   │   ├── documents/              # Feature components (Card #08) ✅
│   │   │   ├── DocumentsTable.tsx
│   │   │   ├── UploadZone.tsx
│   │   │   └── DocumentDetailModal.tsx
│   │   ├── contests/               # Feature components (Card #10) ✅
│   │   │   ├── ContestTable.tsx
│   │   │   ├── ContestCreateStepper.tsx
│   │   │   ├── ContestTimeline.tsx
│   │   │   ├── ContestItemTable.tsx
│   │   │   ├── CommunicationThread.tsx
│   │   │   ├── PaymentForm.tsx
│   │   │   ├── SuccessFeeCalculator.tsx
│   │   │   └── ContestPDFViewer.tsx
│   │   └── reports/                # Feature components (Card #11) ✅
│   │       ├── ReportDashboard.tsx     # 4 KPI cards + 4 Recharts graphs
│   │       ├── ReportFilters.tsx       # Period, date range, carrier/client/status/rule selects
│   │       ├── KPIChart.tsx            # TimeSeries, TopCarriers, TopRules, Severity charts
│   │       ├── ExportPanel.tsx         # PDF/Excel export with filter summary + KPI preview
│   │       ├── ScheduleForm.tsx        # Weekly frequency, day/hour, format, recipients
│   │       └── ScheduleList.tsx        # CRUD with dropdown actions (preview, edit, toggle, delete)
│   ├── hooks/
│   │   ├── index.ts                # Barrel exports
│   │   ├── useApi.ts               # TanStack Query wrapper ✅
│   │   ├── useDiscrepancyActions.ts # Bulk actions, review, export ✅
│   │   ├── useContestWorkflow.ts   # 10 workflow hooks (send, negotiate, payments, PDF, communications, evidence, success fee) ✅ (Card #10)
│   │   └── useReports.ts           # 7 report hooks (dashboard, pdf, excel, schedules CRUD) ✅ (Card #11)
│   ├── layouts/
│   │   ├── index.ts                # Barrel exports
│   │   ├── MainLayout.tsx          # Sidebar + header + outlet ✅
│   │   └── AuthLayout.tsx          # Centered card layout ✅
│   ├── pages/
│   │   ├── index.ts                # Barrel exports
│   │   ├── Login.tsx               # Form + validation ✅
│   │   ├── Register.tsx            # Multi-step form ✅
│   │   ├── Dashboard.tsx           # KPI grid + chart placeholders ✅
│   │   ├── Documents.tsx           # Upload + List + Detail ✅ (Card #08)
│   │   ├── DiscrepanciesPage.tsx   # List + Filters + Detail + Bulk ✅ (Card #09)
│   │   ├── ContestsPage.tsx        # List + Filters + Stats + Create Modal ✅ (Card #10)
│   │   ├── ContestCreatePage.tsx   # 3-step stepper ✅ (Card #10)
│   │   ├── ContestDetailPage.tsx   # Timeline + Items + Comms + Payments ✅ (Card #10)
│   │   ├── ContestNegotiatePage.tsx # Status + Communication + Payment ✅ (Card #10)
│   │   ├── ReportsPage.tsx         # Dashboard/Export/Schedule tabs ✅ (Card #11)
│   │   ├── ReportExportPage.tsx    # Direct export with URL-synced filters ✅ (Card #11)
│   │   ├── Clients.tsx             # 🔴 ComingSoon
│   │   ├── Carriers.tsx            # 🔴 ComingSoon
│   │   ├── Contracts.tsx           # 🔴 ComingSoon
│   │   ├── Settings.tsx            # 🔴 ComingSoon
│   │   └── Profile.tsx             # 🔴 ComingSoon
│   ├── test/                       # Testing infrastructure (Card #01) ✅
│   │   ├── index.ts                # Barrel exports
│   │   ├── setupTests.ts           # MSW server, jest-axe, mocks
│   │   ├── handlers.ts             # MSW handlers for all APIs
│   │   ├── factories.ts            # Test data factories (@faker-js/faker)
│   │   └── msw.test.ts             # MSW integration tests
│   └── types/
│       └── index.ts                # Barrel exports (needs types) - Card #27
├── index.html
├── package.json
├── vite.config.ts                  # Proxy: /api → localhost:8000
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
└── vitest.config.ts                # Vitest config with coverage thresholds
```

---

## 🔧 Development Commands

```bash
cd frontend

pnpm install          # Install deps (run from root: pnpm install)
pnpm dev              # Start dev server (port 3000)
pnpm build            # TypeScript + Vite build
pnpm lint             # ESLint
pnpm test             # Vitest (after Card #01)
pnpm test:ui          # Vitest UI
pnpm test:coverage    # Coverage report
```

---

## 🎨 Design System (Use Existing Components from `index.css`)

### Component Classes (from `@layer components`)
```css
/* Buttons */
.btn, .btn-primary, .btn-secondary, .btn-ghost, .btn-danger
.btn-sm, .btn-lg

/* Forms */
.input, .input-error, .label

/* Layout */
.card, .card-header, .card-body, .card-footer
.page-header, .page-title, .page-subtitle
.section, .grid-kpi

/* Data Display */
.kpi-card, .kpi-value, .kpi-label, .kpi-trend
.badge, .badge-success, .badge-warning, .badge-danger, .badge-primary, .badge-secondary
.table-container, .table, .table th, .table td

/* Navigation */
.sidebar-link, .sidebar-link-active
.tabs-trigger, .tabs-trigger-active
.dropdown-item

/* Modals */
.modal-overlay, .modal-content, .modal-header, .modal-body, .modal-footer

/* States */
.empty-state, .empty-state-icon, .empty-state-title, .empty-state-description
```

### Existing Components (in `src/components/`)
```tsx
// All use design system classes + Radix UI primitives
<Button variant="primary" size="md" loading={false} icon={<Icon />} />
<Input label="Email" error={errors.email} />
<Card><Card.Header /><Card.Body /><Card.Footer /></Card>
<Badge variant="success" />  // success|warning|danger|primary|secondary
<Table><Table.Header /><Table.Body /><Table.Footer /></Table>
<Modal><Modal.Header /><Modal.Body /><Modal.Footer /></Modal>
<DropdownMenu><DropdownMenu.Trigger /><DropdownMenu.Content /><DropdownMenu.Item /></DropdownMenu>
<Avatar src={url} fallback="JD" />
```

### Feature Components (Recently Added)
```tsx
// Discrepancies (Card #09)
<DiscrepanciesTable discrepancies={data} onSort={} onPageChange={} />
<DiscrepancyFilters onFilterChange={} />
<DiscrepancyDetailModal discrepancy={} isOpen={} onClose={} />
<DiscrepancySummaryCards summary={} />
<BulkActionBar selectedIds={} onBulkAction={} />

// Documents (Card #08)
<DocumentsTable documents={} onSort={} onPageChange={} onDetail={} />
<UploadZone onUpload={} />
<DocumentDetailModal document={} isOpen={} onClose={} />

// Contests (Card #10)
<ContestTable contests={} onSelect={} onSend={} onNegotiate={} onViewPDF={} onDownloadPDF={} />
<ContestCreateStepper initialDiscrepancyIds={} onComplete={} onCancel={} />
<ContestTimeline contest={} />
<ContestItemTable items={} />
<CommunicationThread communications={} onAddCommunication={} onDownloadAttachment={} contestId={} />
<PaymentForm contestId={} onSubmit={} />
<SuccessFeeCalculator contractSuccessFeePct={} totalRecovered={} />
<ContestPDFViewer pdfUrl={} onDownload={} />

// Reports (Card #11)
<ReportDashboard data={} isLoading={} />
<ReportFilters filters={} onFiltersChange={} onClearFilters={} hasActiveFilters={} />
<KPIChart type="timeseries" data={} />
<KPIChart type="topcarriers" data={} />
<KPIChart type="toprules" data={} />
<KPIChart type="severity" data={} />
<ExportPanel filters={} kpis={} onExportPDF={} onExportExcel={} />
<ScheduleForm initialData={} onSubmit={} onCancel={} isSubmitting={} />
<ScheduleList schedules={} onEdit={} onToggle={} onDelete={} onPreview={} isLoading={} />
```

### Utility Functions (from `utils/helpers.ts`)
```typescript
cn()                    // clsx + tailwind-merge
formatCurrency()        // BRL formatting
formatNumber(), formatPercent()
formatDate(), formatDateTime(), formatRelativeTime()
hasRole(), ROLE_HIERARCHY  // ADMIN(4) > MANAGER(3) > AUDITOR(2) > CLIENT(1)
getStatusBadge()        // For DiscrepancyStatus, ContestStatus, DocumentStatus
getSeverityBadge()      // LOW, MEDIUM, HIGH, CRITICAL
```

---

## 🔐 Auth System (Use Existing)

```typescript
// Hook - already implemented
const { user, isLoading, isAuthenticated, login, register, logout, hasRole, hasAnyRole } = useAuth()

// Role checks
hasRole('ADMIN')                    // true if user is ADMIN
hasAnyRole(['ADMIN', 'MANAGER'])    // true if user has any of these roles

// API calls auto-include Bearer token via axios interceptors
// Token refresh handled automatically on 401
```

---

## 📡 API Contract (Backend at `localhost:8000`)

### Base URL: `/api/v1` (proxied via Vite to `http://localhost:8000`)

| Module | Endpoints | Status |
|--------|-----------|--------|
| **Auth** | `POST /auth/login`, `POST /auth/register`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me` | ✅ Ready |
| **Documents** | `POST /documents/upload`, `GET /documents`, `GET /documents/{id}`, `POST /documents/{id}/reprocess` | ✅ Ready |
| **Discrepancies** | `GET /discrepancies`, `GET /discrepancies/summary`, `PATCH /discrepancies/bulk-status`, `POST /discrepancies/{id}/review` | ✅ Ready |
| **Contests** | `POST /contests`, `GET /contests`, `GET /contests/{id}`, `POST /contests/{id}/send`, `PATCH /contests/{id}/negotiate`, `POST /contests/{id}/payments` | ✅ Ready |
| **Reports** | `GET /reports/dashboard`, `GET /reports/pdf`, `GET /reports/excel`, `POST /reports/schedule` | ✅ Ready |
| **Settings** | Companies, Users, Carriers, Contracts, Notifications CRUD | ✅ Ready |
| **Clients** | CRUD endpoints | ✅ Ready |
| **Carriers** | CRUD endpoints | ✅ Ready |
| **Contracts** | CRUD + FreightTable endpoints | ✅ Ready |

---

## 🎯 Updated Card Execution Order (Based on Actual State)

### ✅ COMPLETED (Remove from Kanban)
- Card #01: Vitest + RTL + MSW Setup → **DONE** (72 tests passing, coverage working)
- Card #02: Auth Pages → **DONE** (Login, Register exist)
- Card #08: Documents Page → **DONE** (Upload + List + Detail + components)
- Card #09: Discrepancies Page → **DONE** (List + Filters + Detail + Bulk + components)
- Card #10: Contests Page → **DONE** (Create + Detail + Negotiate + Payments + 8 components + 10 hooks)
- Card #11: Reports Page → **DONE** (Dashboard + Export + Schedule + 7 components + Tabs/Select/Switch/KPICard)

### 🔴 SPRINT 1 PRIORITY (Start Here)
| Card | Title | Actual Work Needed |
|------|-------|-------------------|
| **#15** | Settings Pages | Replace `ComingSoon` → Company/Users/Carriers/Contracts/Notifications |

### 🟡 SPRINT 2
| Card | Title | Actual Work Needed |
|------|-------|-------------------|
| **#22** | Clients Page | Replace `ComingSoon` → CRUD (list, create, edit, detail) |
| **#23** | Carriers Page | Replace `ComingSoon` → CRUD (list, create, edit, detail) |
| **#24** | Contracts Page | Replace `ComingSoon` → CRUD + FreightTable editor |
| **#25** | Profile Page | Replace `ComingSoon` → User profile management |
| **#03** | Dashboard Charts | Add Recharts to existing Dashboard |
| **#07** | Design System Enhancements | Tooltip, Toast, Tabs, Select, Pagination, EmptyState, KPICard |

### 🟢 SPRINT 3+ (Technical Debt)
| Card | Title |
|------|-------|
| #26 | Code Splitting & Bundle Optimization (995kB → <500kB) |
| #27 | TypeScript Types Barrel Exports |

---

## 🎯 Card Execution Protocol

### For EACH Card:
1. **Read the Card** in `cards/frontend/ready/XX-title.md`
2. **Move to `in-progress/`**: `mv cards/frontend/ready/XX.md cards/frontend/in-progress/XX.md`
3. **Implement** replacing `ComingSoon` placeholder with full feature
4. **Write Tests** (after Card #01) - unit + integration
5. **Run Quality Gates**: `pnpm lint && pnpm build && pnpm test`
6. **Move to `review/`**: `mv cards/frontend/in-progress/XX.md cards/frontend/review/XX.md`
7. **Update This Agent** with new patterns/components created

### Quality Gates (Must Pass)
```bash
pnpm lint          # ESLint - zero errors
pnpm build         # tsc + vite build - zero errors  
pnpm test          # Vitest - all pass (after Card #01)
pnpm test:coverage # Coverage thresholds (70% lines, 70% functions, 60% branches)
```

---

## 🔄 Coordination with Other Agents

| Agent | Interaction |
|-------|-------------|
| **Tech Lead** | Reviews PRs, approves architecture, moves cards to `done/` |
| **Backend** | Owns OpenAPI spec → you use types; joint spec review for new features |
| **Frontend Specialized Agents** | **Delegate to specialists** (see below) |

### Frontend Specialized Agents (Delegate for Deep Work)
| Agent | Location | When to Delegate |
|-------|----------|------------------|
| **ui-agent** | `agents/frontend/ui/ui-agent.md` | New components, design system, charts, accessibility |
| **pages-agent** | `agents/frontend/pages/pages-agent.md` | Page implementations (Contests, Reports, Settings, Clients, etc.) |
| **state-agent** | `agents/frontend/state/state-agent.md` | New hooks, API endpoints, Zod schemas, TypeScript types |
| **testing-agent** | `agents/frontend/testing/testing-agent.md` | Component tests, hook tests, integration tests, a11y |

### Delegation Examples
```python
# New design system component
Agent(subagent_type="frontend-ui-agent", prompt="Create Toast component using Radix Toast")

# Implement Contests page
Agent(subagent_type="frontend-pages-agent", prompt="Replace Contests ComingSoon with full implementation: list, create, detail, negotiate, payments")

# Create hooks for Contests
Agent(subagent_type="frontend-state-agent", prompt="Create useContests hooks: list, detail, create, negotiate, payments")

# Write tests for Reports page
Agent(subagent_type="frontend-testing-agent", prompt="Write full test suite for Reports page: components, hooks, integration")
```

---

## 📝 Agent Self-Update Protocol (MANDATORY)

**After completing EACH card:**
1. Update this file with:
   - New pages/components created
   - New hooks created
   - New patterns discovered
   - Any API contract changes
2. Move card: `in-progress/` → `review/`
3. Commit: `feat(frontend): Card #XX - [title]`

---

## 🚀 Quick Start for Next Session

```bash
# 1. Check current card
ls cards/frontend/in-progress/ || ls cards/frontend/ready/ | head -5

# 2. START WITH CARD #11 (Reports Page)
cat cards/frontend/ready/11-frontend-reports-pages.md

# 3. Run dev server
cd frontend && pnpm dev
```

**Next Priority:** Card #11 - Reports Page (PDF/Excel export, scheduling)
- Uses: MSW handlers, factories, design system components
- API: `/api/v1/reports` endpoints
- Components needed: Table, Modal, Forms, Export buttons, Scheduler

---

## 📚 Key References

| Document | Purpose |
|----------|---------|
| `cards/frontend/done/01-frontend-qa-setup-vitest-rtl-msw.md` | **START HERE** - Card #01 (DONE) |
| `cards/frontend/done/08-frontend-documents-pages.md` | **DONE** - Card #08 Documents |
| `cards/frontend/done/09-frontend-discrepancies-pages.md` | **DONE** - Card #09 Discrepancies |
| `cards/frontend/ready/10-frontend-contests-pages.md` | **NEXT** - Card #10 Contests |
| `TECHLEAD_REVIEW.md` | Full architectural review |
| `frontend/src/index.css` | Complete design system |
| `frontend/src/utils/helpers.ts` | All utilities |
| `frontend/src/App.tsx` | Routing + layouts |
| `backend/README.md` | Backend API spec |
| `agents/frontend/README.md` | Frontend agents structure |
| `agents/frontend/ui/ui-agent.md` | UI/Design System specialist |
| `agents/frontend/pages/pages-agent.md` | Pages/Features specialist |
| `agents/frontend/state/state-agent.md` | State/API/Forms specialist |
| `agents/frontend/testing/testing-agent.md` | Testing specialist |

---

*This agent owns 100% of frontend completion. After each card: update this file, move card, commit.*