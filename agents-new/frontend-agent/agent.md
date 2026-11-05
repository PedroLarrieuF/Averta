---
name: averta-frontend-agent
description: Dedicated 100% Frontend Agent for AvertaSaaS - React + Vite + TypeScript + Tailwind + Radix UI. Owns all frontend Kanban cards.
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents, Agent
---

# AvertaSaaS Frontend Agent (Dedicated v2.8 - 11/12 Pages Complete)

> **Location:** `frontend/` (moved from `packages/frontend/` on 2026-11-01)
> **Mission:** Complete the frontend for freight audit SaaS - replace all placeholder pages with full implementations
> **Standard:** After each card completion, update this agent + move card to `review/`
> **Last Updated:** 2026-11-05 (Card #26 Code Splitting completed, Card #38 NF-e Dashboard available)

---

## 🎯 ACTUAL Current State (2026-11-03)

### ✅ Already Built (DO NOT REBUILD)
| Area | Status | Files |
|------|--------|-------|
| **Routing & Layouts** | ✅ COMPLETE | `App.tsx`, `MainLayout`, `AuthLayout`, `DeveloperLayout`, Protected/Public routes (lazy-loaded) |
| **Auth Pages** | ✅ COMPLETE | `Login.tsx`, `Register.tsx` (with forms, validation) |
| **Dashboard** | ✅ COMPLETE | `Dashboard.tsx` (KPI cards, charts placeholder) |
| **Documents Page** | ✅ COMPLETE (Card #08) | `Documents.tsx` + `DocumentsTable`, `UploadZone`, `DocumentDetailModal` |
| **Discrepancies Page** | ✅ COMPLETE (Card #09) | `DiscrepanciesPage.tsx` + 5 components (Table, Filters, DetailModal, SummaryCards, BulkActionBar) |
| **Contests Page** | ✅ COMPLETE (Card #10) | `ContestsPage.tsx`, `ContestCreatePage.tsx`, `ContestDetailPage.tsx`, `ContestNegotiatePage.tsx` + 8 components (Table, CreateStepper, Timeline, ItemTable, CommunicationThread, PaymentForm, SuccessFeeCalculator, PDFViewer) |
| **Reports Page** | ✅ COMPLETE (Card #11) | `ReportsPage.tsx`, `ReportExportPage.tsx` + 7 components (Dashboard, Filters, KPIChart, ExportPanel, ScheduleForm, ScheduleList) + Tabs, Select, Switch, KPICard design system components |
| **Settings Pages** | ✅ COMPLETE (Card #15) | `SettingsLayout.tsx`, `CompanySettingsPage.tsx`, `UsersPage.tsx`, `CarriersPage.tsx`, `ContractsPage.tsx`, `NotificationsPage.tsx` + components: `UserInviteModal.tsx`, `ContractForm.tsx`, `FreightTableEditor.tsx` |
| **Clients Page** | ✅ COMPLETE (Card #22) | `Clients.tsx` + 5 components (`ClientsTable`, `ClientForm`, `ClientDetailModal`, `BranchForm`, `BranchesTable`) + 4 branch hooks |
| **Carriers Page** | ✅ COMPLETE (Card #23) | `Carriers.tsx` + 5 components (`CarriersTable`, `CarrierForm`, `CarrierDetailModal`, `BranchForm`, `BranchesTable`) + 4 branch hooks |
| **Contracts Page** | ✅ COMPLETE (Card #24) | `Contracts.tsx` + 6 components (`ContractsTable`, `ContractForm`, `ContractDetailModal`, `FreightTableEditor`, `FreightTableGrid`, `FreightTableVersionManager`) + 12 hooks in `useContracts.ts` |
| **Developer Portal** | ✅ COMPLETE (Card #40) | `DeveloperDashboard.tsx`, `DeveloperDocs.tsx`, `DeveloperKeys.tsx`, `DeveloperAnalytics.tsx`, `DeveloperWebhooks.tsx` + `DeveloperLayout.tsx` |
| **Profile Page** | ✅ COMPLETE (Card #25) | `Profile.tsx` + 5 components (`ProfileHeader`, `ProfileForm`, `ChangePasswordModal`, `NotificationPreferences`, `DangerZone`) + 6 hooks in `useApi.ts` |
| **Design System Components** | ✅ COMPLETE | `Button`, `Input`, `Card`, `Badge`, `Table`, `Modal`, `DropdownMenu`, `Avatar`, `Tabs`, `Select`, `Switch`, `KPICard`, `Tooltip`, `Toast`, `Pagination`, `EmptyState`, `PageSkeleton` |
| **Auth System** | ✅ COMPLETE | `auth-context.tsx`, `auth-storage.ts`, `useAuth()` hook |
| **API Client** | ✅ COMPLETE | `api.ts` (axios + interceptors + token refresh) |
| **Utilities** | ✅ COMPLETE | `helpers.ts` (formatters, roles, badges, cn) |
| **Hooks** | ✅ PARTIAL | `useApi.ts` (TanStack Query wrapper), `useDiscrepancyActions.ts`, `useSettings.ts`, `useContracts.ts` |
| **Testing Infrastructure** | ✅ COMPLETE (Card #01) | Vitest + RTL + MSW + jest-axe + @faker-js/faker (72 tests passing) |
| **Bundle Optimization** | ✅ COMPLETE (Card #26) | `vite.config.ts` (manualChunks), `App.tsx` (lazy routes + Suspense), `PageSkeleton.tsx` |

### 🔴 NEEDS IMPLEMENTATION (Replace Placeholders)
| Page | Card | Priority | Current State |
|------|------|----------|---------------|
| **NF-e Dashboard** | #38 | 🔴 HIGH | **NEW** - Rules dashboard, discrepancy views, validation table, admin config |

### 🟡 NEEDS ENHANCEMENT
| Area | Card | Current State |
|------|------|---------------|
| **Dashboard Charts** | #03 | Placeholder - needs Recharts implementation |
| **Design System** | #07 | Components exist but need: Tooltip, Toast, Pagination, EmptyState (Tabs, Select, Switch, KPICard ✅ done in Card #11) |
| **TypeScript Types** | #27 | Missing barrel exports in `frontend/src/types/index.ts` (in review) |

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
| #08 | Documents Page (Upload + List + Detail) | ✅ **Done** | CRITICAL | L |
| #09 | Discrepancies Page (List + Filters + Detail + Bulk) | ✅ **Done** | CRITICAL | L |
| #10 | Contests Page (create/detail/negotiate/pay) | ✅ **Done** | CRITICAL | XL |
| #11 | Reports Page (PDF/Excel export, scheduling) | ✅ **Done** | HIGH | L |
| #15 | Settings Pages (Company/Users/Carriers/Contracts/Notifications) | ✅ **Done** | HIGH | XL |
| #21 | Reports Page (NEW - detailed spec) | ✅ **Done** (merged into #11) | HIGH | L |
| #22 | Clients Page (CRUD) | ✅ **Done** | HIGH | M |
| #23 | Carriers Page (CRUD) | ✅ **Done** | HIGH | M |
| #24 | Contracts Page (CRUD + FreightTable editor) | ✅ **Done** | HIGH | L |
| #25 | Profile Page (user profile management) | ✅ **Done** | MEDIUM | S |
| #26 | Code Splitting & Bundle Optimization | ✅ **Done** | MEDIUM | M |
| #27 | TypeScript Types Barrel Exports | 🔴 Ready (in review) | LOW | S |
| #38 | NF-e Rules Dashboard & Discrepancy Views | 🔴 **Ready (NEW)** | HIGH | L |
| #40 | Developer Portal (Dashboard, Docs, Keys, Analytics, Webhooks) | ✅ **Done** | CRITICAL | L |

### Card Lifecycle (This Agent Owns)
1. **Tech Lead assigns** → Card moved to `ready/`
2. **Agent picks up** → Move to `in-progress/`, start implementation
3. **Implementation complete** → Move to `review/`, notify Tech Lead
4. **Tech Lead approves** → Move to `done/`, update this agent.md

---

## 📁 Project Structure (Actual - 2026-11-05)

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
│   │   ├── Tabs.tsx                # Radix Tabs
│   │   ├── Select.tsx              # Radix Select
│   │   ├── Switch.tsx              # Radix Switch
│   │   ├── KPICard.tsx             # KPI display card
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
│   │   ├── reports/                # Feature components (Card #11) ✅
│   │   │   ├── ReportDashboard.tsx     # 4 KPI cards + 4 Recharts graphs
│   │   │   ├── ReportFilters.tsx       # Period, date range, carrier/client/status/rule selects
│   │   │   ├── KPIChart.tsx            # TimeSeries, TopCarriers, TopRules, Severity charts
│   │   │   ├── ExportPanel.tsx         # PDF/Excel export with filter summary + KPI preview
│   │   │   ├── ScheduleForm.tsx        # Weekly frequency, day/hour, format, recipients
│   │   │   └── ScheduleList.tsx        # CRUD with dropdown actions (preview, edit, toggle, delete)
│   │   └── settings/               # Feature components (Card #15) ✅
│   │       ├── UserInviteModal.tsx
│   │       ├── ContractForm.tsx
│   │       └── FreightTableEditor.tsx
│   │   ├── contracts/                # Feature components (Card #24) ✅
│   │       ├── ContractsTable.tsx
│   │       ├── ContractForm.tsx
│   │       ├── ContractDetailModal.tsx
│   │       ├── FreightTableEditor.tsx
│   │       ├── FreightTableGrid.tsx
│   │       └── FreightTableVersionManager.tsx
│   ├── hooks/
│   │   ├── index.ts                # Barrel exports
│   │   ├── useApi.ts               # TanStack Query wrapper ✅
│   │   ├── useDiscrepancyActions.ts # Bulk actions, review, export ✅
│   │   ├── useContestWorkflow.ts   # 10 workflow hooks (send, negotiate, payments, PDF, communications, evidence, success fee) ✅ (Card #10)
│   │   ├── useReports.ts           # 7 report hooks (dashboard, pdf, excel, schedules CRUD) ✅ (Card #11)
│   │   ├── useSettings.ts          # 15 settings hooks (users, carriers, contracts, company, notifications, freight tables) ✅ (Card #15)
│   │   └── useContracts.ts         # 12 contracts/freight tables hooks (CRUD + reference data) ✅ (Card #24)
│   ├── layouts/
│   │   ├── index.ts                # Barrel exports
│   │   ├── MainLayout.tsx          # Sidebar + header + outlet ✅
│   │   ├── AuthLayout.tsx          # Centered card layout ✅
│   │   └── DeveloperLayout.tsx     # Developer Portal sidebar + header ✅ (Card #40)
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
│   │   ├── Clients.tsx             # CRUD + Branches ✅ (Card #22)
│   │   ├── Carriers.tsx            # CRUD + Branches ✅ (Card #23)
│   │   ├── Contracts.tsx           # ✅ CRUD + FreightTable editor (Card #24)
│   │   ├── developer/              # Developer Portal (Card #40) ✅
│   │   │   ├── index.ts            # Barrel exports
│   │   │   ├── DeveloperDashboard.tsx  # KPIs, Quick Actions, Usage Chart
│   │   │   ├── DeveloperDocs.tsx       # Scalar API Documentation
│   │   │   ├── DeveloperKeys.tsx       # API Key Management (CRUD)
│   │   │   ├── DeveloperAnalytics.tsx  # Usage Analytics & Charts
│   │   │   └── DeveloperWebhooks.tsx   # Webhook Management (CRUD)
│   │   ├── settings/               # Settings pages (Card #15) ✅
│   │   │   ├── SettingsLayout.tsx
│   │   │   ├── CompanySettingsPage.tsx
│   │   │   ├── UsersPage.tsx
│   │   │   ├── CarriersPage.tsx
│   │   │   ├── ContractsPage.tsx
│   │   │   └── NotificationsPage.tsx
│   │   └── Profile.tsx             # 🔴 ComingSoon
│   ├── test/                       # Testing infrastructure (Card #01) ✅
│   │   ├── index.ts                # Barrel exports
│   │   ├── setupTests.ts           # MSW server, jest-axe, mocks
│   │   ├── handlers.ts             # MSW handlers for all APIs
│   │   ├── factories.ts            # Test data factories (@faker-js/faker)
│   │   └── msw.test.ts             # MSW integration tests
│   └── types/
│       └── index.ts                # Barrel exports (needs types) - Card #27
├── public/
│   └── openapi/
│       └── v1.yaml                 # OpenAPI 3.1 spec for Scalar docs ✅ (Card #40)
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

// Settings (Card #15)
<UserInviteModal open={} onOpenChange={} onSubmit={} isSubmitting={} />
<ContractForm initialData={} clients={} carriers={} onSubmit={} onCancel={} isSubmitting={} mode={} />
<FreightTableEditor initialRules={} onSave={} onCancel={} isSubmitting={} />
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
- Card #15: Settings Pages → **DONE** (Company/Users/Carriers/Contracts/Notifications + 3 components + 8 hooks)
- Card #22: Clients Page → **DONE** (CRUD + Branches + 5 components + 4 hooks)
- Card #23: Carriers Page → **DONE** (CRUD + Branches + 5 components + 4 hooks)
- Card #24: Contracts Page → **DONE** (CRUD + FreightTable Editor + 6 components + 12 hooks)
- Card #25: Profile Page → **DONE** (Profile management + components + hooks)
- Card #26: Code Splitting & Bundle Optimization → **DONE** (Lazy routes, Suspense, PageSkeleton, manualChunks)
- Card #40: Developer Portal → **DONE** (Dashboard, Docs, Keys, Analytics, Webhooks + 5 pages + Layout)

### 🔴 SPRINT 1 PRIORITY (Start Here)
| Card | Title | Actual Work Needed |
|------|-------|-------------------|
| *All Sprint 1 cards completed* | | |

### 🟡 SPRINT 2
| Card | Title | Actual Work Needed |
|------|-------|-------------------|
| **#38** | **NF-e Dashboard & Discrepancy Views** | **NEW FEATURE** - Rules dashboard, discrepancy detail, validation table, admin config (4 components + hooks + types) |
| **#03** | Dashboard Charts | Add Recharts to existing Dashboard |
| **#07** | Design System Enhancements | Tooltip, Toast, Tabs, Select, Pagination, EmptyState, KPICard |

### 🟢 SPRINT 3+ (Technical Debt)
| Card | Title |
|------|-------|
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

# 2. Next Cards Available:
#    Card #38 - NF-e Dashboard & Discrepancy Views (Sprint 2, High) - NEW FEATURE
#    Card #03 - Dashboard Charts (Sprint 2, High)
#    Card #07 - Design System Enhancements (Sprint 2, High)
#    Card #27 - TypeScript Types Barrel Exports (Sprint 3, Low)

# 3. Run dev server
cd frontend && pnpm dev
```

**Next Priority:** Card #38 - NF-e Dashboard & Discrepancy Views (NEW FEATURE)
- Route: `/nfe/rules`, `/nfe/discrepancies/:id`, `/admin/nfe/rules`
- Components: NFERulesDashboard, NFEDiscrepancyDetail, NFEValidationTable, NFERuleConfig
- API: `/api/v1/nfe/rules`, `/api/v1/nfe/discrepancies` (backend cards #34, #35, #36 done)
- Types: NF-e rules (5 Critical, 7 High, 6 Medium), discrepancy details with XML data
- Backend dependencies: Cards #34, #35, #36 (all DONE)

**Alternative Next:** Card #25 - Profile Page (User profile management)
- Uses: Design system components, auth hooks, API
- API: `/api/v1/users/me`, `/api/v1/users/{id}`
- Components needed: ProfileForm, ChangePasswordModal, NotificationPreferences, DangerZone

**Recently Completed:** Card #26 - Code Splitting & Bundle Optimization
- All 21 pages lazy-loaded with React.lazy() + Suspense boundaries
- PageSkeleton & PageSkeletonMinimal fallback components created
- Vite manualChunks: 7 vendor bundles (react-vendor, radix-vendor, query-vendor, charts-vendor, forms-vendor, utils-vendor, ui-vendor)
- cssCodeSplit: true, chunkSizeWarningLimit: 500
- Build passes, lint passes

**Recently Completed:** Card #24 - Contracts Page
- Full CRUD: List (with pagination, filters, search), Create, Edit, Detail, Delete
- FreightTable Editor: Spreadsheet-like grid with 4 modals (Rodoviário, Aéreo, Marítimo, Ferroviário)
- Version management with history and comparison
- 6 new components + 12 hooks in useContracts.ts
- Types: Contract, FreightTable, FreightRate with enums

**Recently Completed:** Card #40 - Developer Portal
- Dashboard with KPIs, Quick Actions, Usage Chart
- Scalar API Documentation (`/developer/docs`)
- API Key Management (`/developer/keys`)
- Usage Analytics (`/developer/analytics`) - 6 SVG charts
- Webhook Management (`/developer/webhooks`)
- DeveloperLayout with sidebar navigation

---

## 📚 Key References

| Document | Purpose |
|----------|---------|
| `cards/frontend/done/01-frontend-qa-setup-vitest-rtl-msw.md` | **START HERE** - Card #01 (DONE) |
| `cards/frontend/done/08-frontend-documents-pages.md` | **DONE** - Card #08 Documents |
| `cards/frontend/done/09-frontend-discrepancies-pages.md` | **DONE** - Card #09 Discrepancies |
| `cards/frontend/done/10-frontend-contests-pages.md` | **DONE** - Card #10 Contests |
| `cards/frontend/done/11-frontend-reports-pages.md` | **DONE** - Card #11 Reports |
| `cards/frontend/review/15-frontend-settings-pages.md` | **DONE** - Card #15 Settings |
| `cards/frontend/review/22-frontend-clients-page.md` | **DONE** - Card #22 Clients |
| `cards/frontend/review/40-frontend-developer-portal.md` | **DONE** - Card #40 Developer Portal |
| `cards/frontend/ready/23-frontend-carriers-page.md` | **NEXT** - Card #23 Carriers |
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