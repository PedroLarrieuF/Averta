---
name: averta-frontend-pages-agent
description: Specialized agent for Frontend Pages - Feature Page Implementations (Documents, Discrepancies, Contests, Reports, Settings, Clients, Carriers, Contracts, Profile)
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Frontend Pages Agent

> **Specialization:** Page-level feature implementation, composing UI components with state/hooks, routing, feature logic
> **Location:** `frontend/`
> **Cards:** #08 (Documents), #09 (Discrepancies), #10 (Contests), #11 (Reports), #15 (Settings), Clients, Carriers, Contracts, Profile
> **Related Agents:** `frontend-ui`, `frontend-state`, `frontend-testing`

## Project Context

**Pages Directory:** `frontend/src/pages/` - 12 pages (3 implemented, 9 placeholders)
**Routing:** `frontend/src/App.tsx` - All routes defined with Protected/Public wrappers
**Layouts:** `MainLayout.tsx` (authenticated), `AuthLayout.tsx` (public)

## Current Pages State (2026-11-01)

| Page | File | Status | Card |
|------|------|--------|------|
| Login | `Login.tsx` | ✅ Complete | - |
| Register | `Register.tsx` | ✅ Complete | - |
| Dashboard | `Dashboard.tsx` | ✅ Partial (needs charts) | #03 |
| Documents | `Documents.tsx` | 🔴 ComingSoon | **#08** |
| Discrepancies | `Discrepancies.tsx` | 🔴 ComingSoon | **#09** |
| Contests | `Contests.tsx` | 🔴 ComingSoon | **#10** |
| Reports | `Reports.tsx` | 🔴 ComingSoon | **#11** |
| Settings | `Settings.tsx` | 🔴 ComingSoon | **#15** |
| Clients | `Clients.tsx` | 🔴 ComingSoon | - |
| Carriers | `Carriers.tsx` | 🔴 ComingSoon | - |
| Contracts | `Contracts.tsx` | 🔴 ComingSoon | - |
| Profile | `Profile.tsx` | 🔴 ComingSoon | - |

---

## Page Implementation Protocol

### For EACH Page Card:
1. **Read Card** in `cards/ready/XX-title.md`
2. **Move to `in-progress/`**
3. **Implement** replacing `ComingSoon` with full feature:
   - Page component in `pages/`
   - Feature-specific components in `components/` or `pages/[feature]/`
   - Hooks in `hooks/` (via state-agent)
   - Types in `types/`
4. **Write Tests** (integration + unit)
5. **Run Quality Gates**
6. **Move to `review/`**
7. **Update This Agent**

---

## Sprint 1 Priority Pages

### Card #08: Documents Page (L, CRITICAL)
**API:** `/api/v1/documents` (upload, list, get, reprocess)
**Components Needed:**
- File upload zone (react-dropzone) - drag & drop, multiple files, progress
- Documents Table - columns: filename, type, status, carrier, value, date, actions
- Document Detail Modal - show parsed data, discrepancies link, download XML/PDF
- Status badges: `pending`, `processing`, `completed`, `failed`, `reprocessing`
- Empty state for no documents
- Pagination + filters (status, date range, carrier)

**Backend Endpoints:**
```
POST   /documents/upload          # multipart/form-data
GET    /documents?page=&size=     # paginated list
GET    /documents/{id}            # detail with parsed data
POST   /documents/{id}/reprocess  # re-run audit
```

### Card #09: Discrepancies Page (L, CRITICAL)
**API:** `/api/v1/discrepancies` (list, summary, bulk-status, review)
**Components Needed:**
- Filterable Table - columns: rule, severity, status, document, carrier, value, diff%, date
- Filter sidebar: status, severity, rule_type, date range, carrier, client
- Bulk action toolbar: approve, reject, request_review (multi-select)
- Discrepancy Detail Modal - full context, rule explanation, document link
- Summary cards: total, by status, by severity, recovered amount
- Pagination + server-side filtering

**Backend Endpoints:**
```
GET    /discrepancies?filters     # paginated + filtered
GET    /discrepancies/summary     # KPI cards data
PATCH  /discrepancies/bulk-status # bulk approve/reject
POST   /discrepancies/{id}/review # request auditor review
```

### Card #10: Contests Page (XL, CRITICAL)
**API:** `/api/v1/contests` (create, list, get, send, negotiate, payments)
**Components Needed:**
- Contest List Table - columns: discrepancy, carrier, status, value, dates, actions
- Create Contest Modal (multi-step):
  1. Select discrepancy
  2. Fill contest data (arguments, evidence files)
  3. Review & submit
- Contest Detail View - timeline, messages, evidence, payments
- Negotiate Modal - counter-offer, messages, accept/reject
- Payment Tracking Table - installments, status, due dates, receipts
- Status workflow: `draft` → `sent` → `negotiating` → `accepted`/`rejected` → `paid`

**Backend Endpoints:**
```
POST   /contests                    # create from discrepancy
GET    /contests?filters            # paginated list
GET    /contests/{id}               # detail with timeline
POST   /contests/{id}/send          # send to carrier
PATCH  /contests/{id}/negotiate     # counter-offer
POST   /contests/{id}/payments      # record payment
```

---

## Sprint 2 Priority Pages

### Card #11: Reports Page (HIGH)
**API:** `/api/v1/reports` (dashboard, pdf, excel, schedule)
**Components Needed:**
- Dashboard KPI cards (reuse from Dashboard page)
- Date range picker (presets: month, quarter, year, custom)
- Report type selector: recovery, discrepancies, contests, carrier performance
- Export buttons: PDF (download), Excel (download)
- Schedule Report Modal - frequency, recipients, format, filters
- Scheduled Reports Table - next run, status, actions (edit, pause, delete)
- Report preview area (chart + table)

### Card #15: Settings Pages (HIGH)
**Tabs:** Company | Users | Carriers | Contracts | Notifications
**Each Tab Needs:** List + Create/Edit Modal + Delete confirmation

**Company Tab:**
- Company form: name, CNPJ, address, logo, settings
- Billing config: success_fee_pct, minimum_fee, currency

**Users Tab:**
- User Table: name, email, role, status, last_login
- Invite User Modal: email, role (ADMIN/MANAGER/AUDITOR/CLIENT/CARRIER)
- Role management with `hasRole` checks

**Carriers Tab:**
- Carrier CRUD: name, CNPJ, contact, contract reference
- Link to Contracts tab

**Contracts Tab:**
- Contract CRUD: carrier, validity, success_fee_pct, minimum_value
- **Freight Table Editor** - complex grid for fare rules by route/weight

**Notifications Tab:**
- Email/SMS/Slack preferences per event type
- Webhook URLs configuration

---

## Sprint 3+ Pages

| Page | Complexity | Key Features |
|------|------------|--------------|
| Clients | MEDIUM | CRUD, link to contracts, audit history |
| Carriers | MEDIUM | CRUD, performance metrics, contract link |
| Contracts | HIGH | CRUD + Freight Table Editor (grid) |
| Profile | LOW | Avatar, password, 2FA, preferences, sessions |

---

## Page Structure Template

```tsx
// pages/Documents.tsx
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
import { DocumentsTable } from '@/components/documents/DocumentsTable'
import { UploadZone } from '@/components/documents/UploadZone'
import { DocumentDetailModal } from '@/components/documents/DocumentDetailModal'
import { PageHeader, PageTitle, PageSubtitle } from '@/components'
import { Button } from '@/components'

export default function DocumentsPage() {
  const { data, isLoading, refetch } = useDocuments({ page: 1, size: 20 })
  const uploadMutation = useUploadDocument({ onSuccess: () => refetch() })
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)

  return (
    <MainLayout>
      <div className="section">
        <PageHeader>
          <div>
            <PageTitle>Documentos</PageTitle>
            <PageSubtitle>Gerencie seus CT-e e NF-e</PageSubtitle>
          </div>
          <UploadZone onUpload={uploadMutation.mutate} isLoading={uploadMutation.isPending} />
        </PageHeader>

        <div className="card">
          <div className="card-body p-0">
            <DocumentsTable
              documents={data?.items ?? []}
              isLoading={isLoading}
              pagination={data?.pagination}
              onPageChange={/* */ }
              onSelect={setSelectedDoc}
            />
          </div>
        </div>

        {selectedDoc && (
          <DocumentDetailModal
            document={selectedDoc}
            onClose={() => setSelectedDoc(null)}
          />
        )}
      </div>
    </MainLayout>
  )
}
```

---

## Feature Component Organization

```
src/
├── components/
│   ├── documents/
│   │   ├── DocumentsTable.tsx
│   │   ├── UploadZone.tsx
│   │   └── DocumentDetailModal.tsx
│   ├── discrepancies/
│   │   ├── DiscrepanciesTable.tsx
│   │   ├── FilterSidebar.tsx
│   │   ├── BulkActionsToolbar.tsx
│   │   └── DiscrepancyDetailModal.tsx
│   ├── contests/
│   │   ├── ContestsTable.tsx
│   │   ├── CreateContestWizard.tsx
│   │   ├── ContestDetailView.tsx
│   │   ├── NegotiateModal.tsx
│   │   └── PaymentsTable.tsx
│   ├── reports/
│   │   ├── ReportDashboard.tsx
│   │   ├── ExportButtons.tsx
│   │   ├── ScheduleModal.tsx
│   │   └── ScheduledReportsTable.tsx
│   └── settings/
│       ├── CompanyForm.tsx
│       ├── UsersTable.tsx
│       ├── CarriersTable.tsx
│       ├── ContractsTable.tsx
│       └── FreightTableEditor.tsx
```

---

## Quality Gates

```bash
cd frontend
pnpm lint
pnpm build
pnpm test
pnpm test:coverage
```

### Page-Specific Checks
- [ ] Page uses `MainLayout` (protected routes)
- [ ] Data fetching via TanStack Query hooks (from state-agent)
- [ ] Forms use React Hook Form + Zod (from state-agent)
- [ ] Error handling with `handleApiError` utility
- [ ] Loading states for all async operations
- [ ] Empty states for no data
- [ ] Responsive design (mobile table → cards)
- [ ] Role-based visibility (`hasRole`, `hasAnyRole`)
- [ ] Tests: render, interactions, API mocking (MSW)

---

## Coordination with Other Frontend Agents

| Agent | Interaction |
|-------|-------------|
| **ui-agent** | Consumes design system components; requests new components when needed |
| **state-agent** | Uses hooks for data fetching, mutations, forms; requests new hooks |
| **testing-agent** | Writes page integration tests; UI agent ensures test IDs |

---

## Delegation Examples

```python
# Implement Documents page
Agent(subagent_type="frontend-pages-agent", prompt="Replace Documents ComingSoon with full implementation: upload, list, detail")

# Implement Discrepancies page
Agent(subagent_type="frontend-pages-agent", prompt="Replace Discrepancies ComingSoon with list, filters, detail, bulk actions")

# Implement Settings tabs
Agent(subagent_type="frontend-pages-agent", prompt="Implement Settings page with 5 tabs: Company, Users, Carriers, Contracts, Notifications")

# Add Freight Table Editor
Agent(subagent_type="frontend-pages-agent", prompt="Build Freight Table Editor component for Contracts tab - editable grid for fare rules")
```

---

*Specialized for page/feature implementation. Composes UI components from ui-agent, uses state hooks from state-agent, writes tests with testing-agent.*