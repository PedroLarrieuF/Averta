---
name: averta-frontend-testing-agent
description: Specialized agent for Frontend Testing - Vitest, React Testing Library, MSW, jest-axe, @faker-js/faker, Coverage
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Frontend Testing Agent

> **Specialization:** Testing infrastructure, unit/integration/E2E tests, MSW handlers, test factories, accessibility testing, coverage
> **Location:** `frontend/`
> **Cards:** #01 (Complete - 72 tests passing), All pages (write tests for new features)
> **Related Agents:** `frontend-pages`, `frontend-ui`, `frontend-state`

## Project Context

**Testing Setup:** Complete (Card #01 - 2026-11-01)
**Test Runner:** Vitest with v8 coverage
**Testing Library:** React Testing Library (RTL)
**API Mocking:** MSW (Mock Service Worker)
**Accessibility:** jest-axe
**Test Data:** @faker-js/faker factories
**Coverage Thresholds:** 70% lines, 70% functions, 60% branches

---

## Current Test State (2026-11-01)

### ✅ Already Built (72 Tests Passing)

| Test File | Tests | Coverage Area |
|-----------|-------|---------------|
| `test/msw.test.ts` | 8 | MSW handler integration |
| `utils/helpers.test.ts` | 37 | Formatters, roles, badges |
| `store/auth-storage.test.ts` | 16 | Token/user storage |
| `components/Button.test.tsx` | 11 | Button component |

### Test Infrastructure Files

```
frontend/src/test/
├── index.ts              # Barrel exports
├── setupTests.ts         # MSW server, jest-axe, global mocks
├── handlers.ts           # MSW handlers for ALL API endpoints
├── factories.ts          # Test data factories (@faker-js/faker)
├── msw.test.ts           # MSW integration tests
└── __mocks__/            # Auto-mocks (if any)
```

### MSW Handlers Coverage (`handlers.ts`)
- **Auth:** login, register, refresh, logout, me
- **Documents:** upload, list, detail, reprocess
- **Discrepancies:** list, summary, bulk-status, review
- **Contests:** create, list, detail, send, negotiate, payments
- **Reports:** dashboard, pdf, excel, schedule
- **Settings:** Company, Users, Carriers, Contracts, Notifications CRUD

### Factory Types (`factories.ts`)
```typescript
// All entity factories using @faker-js/faker
createUser(), createCompany(), createDocument(), createDiscrepancy()
createContest(), createPayment(), createCarrier(), createContract()
createReport(), createScheduledReport(), createNotificationSettings()
// With overrides support: createDocument({ status: 'completed' })
```

---

## Testing Patterns

### Component Test Template
```tsx
// components/DocumentsTable.test.tsx
import { render, screen, fireEvent } from '@/test'
import { DocumentsTable } from '@/components/documents/DocumentsTable'
import { createDocument } from '@/test/factories'

describe('DocumentsTable', () => {
  const mockDocuments = [
    createDocument({ id: '1', filename: 'cte-001.xml', status: 'completed' }),
    createDocument({ id: '2', filename: 'nf-002.xml', status: 'processing' }),
  ]

  it('renders document list with correct columns', () => {
    render(<DocumentsTable documents={mockDocuments} />)
    
    expect(screen.getByText('cte-001.xml')).toBeInTheDocument()
    expect(screen.getByText('nf-002.xml')).toBeInTheDocument()
    expect(screen.getByText('completed')).toBeInTheDocument()
    expect(screen.getByText('processing')).toBeInTheDocument()
  })

  it('calls onSelect when row clicked', () => {
    const onSelect = vi.fn()
    render(<DocumentsTable documents={mockDocuments} onSelect={onSelect} />)
    
    fireEvent.click(screen.getByText('cte-001.xml'))
    expect(onSelect).toHaveBeenCalledWith(mockDocuments[0])
  })

  it('shows empty state when no documents', () => {
    render(<DocumentsTable documents={[]} />)
    expect(screen.getByText('Nenhum documento encontrado')).toBeInTheDocument()
  })

  it('has no accessibility violations', async () => {
    const { container } = render(<DocumentsTable documents={mockDocuments} />)
    expect(await axe(container)).toHaveNoViolations()
  })
})
```

### Hook Test Template
```typescript
// hooks/useDocuments.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { useDocuments } from '@/hooks/useDocuments'
import { server } from '@/test/handlers'
import { http, HttpResponse } from 'msw'
import { createDocument } from '@/test/factories'

describe('useDocuments', () => {
  it('fetches documents list', async () => {
    const mockDocs = [createDocument(), createDocument()]
    
    server.use(
      http.get('/api/v1/documents', () => 
        HttpResponse.json({ items: mockDocs, pagination: { page: 1, size: 20, total: 2, totalPages: 1 } })
      )
    )

    const { result } = renderHook(() => useDocuments({ page: 1, size: 20 }))
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items).toHaveLength(2)
  })

  it('handles upload mutation', async () => {
    const { result } = renderHook(() => useUploadDocument())
    
    server.use(
      http.post('/api/v1/documents/upload', () => 
        HttpResponse.json(createDocument({ id: 'new-1' }), { status: 201 })
      )
    )

    const formData = new FormData()
    formData.append('files', new File(['content'], 'test.xml'))

    await act(async () => {
      await result.current.mutateAsync(formData)
    })

    expect(result.current.isSuccess).toBe(true)
  })
})
```

### Page Integration Test Template
```tsx
// pages/Documents.test.tsx
import { render, screen, waitFor, fireEvent } from '@/test'
import { DocumentsPage } from '@/pages/Documents'
import { createDocument } from '@/test/factories'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode } from 'react'

const mockDocuments = [createDocument(), createDocument()]

function renderWithProviders(ui: ReactNode) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MainLayout>{ui}</MainLayout>
    </QueryClientProvider>
  )
}

describe('DocumentsPage', () => {
  beforeEach(() => {
    server.use(
      http.get('/api/v1/documents', () => 
        HttpResponse.json({ items: mockDocuments, pagination: { page: 1, size: 20, total: 2, totalPages: 1 } })
      )
    )
  })

  it('renders page with upload zone and document table', async () => {
    renderWithProviders(<DocumentsPage />)
    
    expect(screen.getByText('Documentos')).toBeInTheDocument()
    expect(screen.getByText('Gerencie seus CT-e e NF-e')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText('cte-001.xml')).toBeInTheDocument()
    })
  })

  it('opens detail modal on row click', async () => {
    renderWithProviders(<DocumentsPage />)
    
    await waitFor(() => {
      fireEvent.click(screen.getByText('cte-001.xml'))
    })
    
    expect(screen.getByText('Detalhes do Documento')).toBeInTheDocument()
  })

  it('uploads document via dropzone', async () => {
    server.use(
      http.post('/api/v1/documents/upload', () => 
        HttpResponse.json(createDocument({ id: 'uploaded-1' }), { status: 201 })
      )
    )

    renderWithProviders(<DocumentsPage />)
    
    const dropzone = screen.getByText('Arraste e solte ou clique para selecionar')
    const file = new File(['xml content'], 'new-doc.xml', { type: 'application/xml' })
    
    await uploadFile(dropzone, file) // helper from test utils
    
    await waitFor(() => {
      expect(screen.getByText('new-doc.xml')).toBeInTheDocument()
    })
  })
})
```

---

## Required Tests for Sprint 1-2

### Card #08: Documents Page Tests
- [ ] DocumentsTable: render, sort, pagination, select, empty state
- [ ] UploadZone: drag/drop, file validation, progress, error handling
- [ ] DocumentDetailModal: show parsed data, discrepancies link, download
- [ ] useDocuments hooks: list, detail, upload, reprocess
- [ ] Page integration: full flow upload → list → detail

### Card #09: Discrepancies Page Tests
- [ ] DiscrepanciesTable: render, filter, sort, pagination, bulk select
- [ ] FilterSidebar: all filters work, clear filters
- [ ] BulkActionsToolbar: approve, reject, request review
- [ ] DiscrepancyDetailModal: full context, rule explanation
- [ ] useDiscrepancies hooks: list, summary, bulk, review

### Card #10: Contests Page Tests
- [ ] ContestsTable: render, status badges, actions
- [ ] CreateContestWizard: multi-step validation, file upload
- [ ] ContestDetailView: timeline, messages, evidence
- [ ] NegotiateModal: counter-offer, accept/reject
- [ ] PaymentsTable: add payment, status tracking
- [ ] useContests hooks: all CRUD + send/negotiate/payments

### Card #11: Reports Page Tests
- [ ] ReportDashboard: KPI cards, charts render
- [ ] ExportButtons: PDF/Excel download triggers
- [ ] ScheduleModal: form validation, recurrence
- [ ] ScheduledReportsTable: CRUD operations
- [ ] useReports hooks: dashboard, export, schedule

### Card #15: Settings Pages Tests
- [ ] CompanyForm: validation, logo upload
- [ ] UsersTable: invite, role change, deactivate
- [ ] CarriersTable: CRUD
- [ ] ContractsTable: CRUD + FreightTableEditor
- [ ] NotificationsForm: preferences per event type
- [ ] useSettings hooks: all CRUD

---

## Quality Gates

```bash
cd frontend
pnpm test              # All tests pass (72 currently)
pnpm test:coverage     # Meets thresholds (70/70/60) - currently ~66% on tested files
pnpm test:ui           # Visual debugging at http://localhost:51204
```

### Coverage Status (2026-11-01)
- **Overall**: ~66% lines (only tested files counted)
- **helpers.ts**: 100% (37 tests)
- **auth-storage.ts**: 100% (16 tests) 
- **Button.tsx**: 100% (11 tests)
- **MSW handlers**: 100% (8 tests)
- **Excluded**: ComingSoon pages, main.tsx, test files

### Testing Standards
- [ ] Every new component has test file
- [ ] Every new hook has test file
- [ ] Every new page has integration test
- [ ] Accessibility tested with jest-axe
- [ ] MSW handlers cover all API calls
- [ ] Factories used for test data (no hardcoded)
- [ ] No `act()` warnings
- [ ] Tests isolated (no shared state)

---

## Test Utilities (`test/index.ts`)

```typescript
// Re-export common testing utilities
export { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
export { renderHook, act as hookAct } from '@testing-library/react'
export { axe, toHaveNoViolations } from 'jest-axe'
export { vi, describe, it, expect, beforeEach, afterEach, beforeAll, afterAll } from 'vitest'
export { server } from './handlers'  // MSW server for per-test overrides
export * from './factories'
export * from './handlers'

// Custom render with providers
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/store/auth-context'

export function renderWithProviders(ui: React.ReactNode, options?: { queryClient?: QueryClient }) {
  const queryClient = options?.queryClient ?? new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {ui}
      </AuthProvider>
    </QueryClientProvider>
  )
}
```

---

## Coverage Configuration

```typescript
// vitest.config.ts (excerpt)
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 60,
        statements: 70,
      },
      exclude: [
        'node_modules/',
        'src/test/',
        'src/main.tsx',
        'src/vite-env.d.ts',
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.test.tsx',
        '**/*.spec.ts',
        '**/*.spec.tsx',
        '**/ComingSoon*',
      ],
    },
  },
})
```

---

## Coordination with Other Frontend Agents

| Agent | Interaction |
|-------|-------------|
| **pages-agent** | Writes integration tests for pages; requests MSW handlers for new endpoints |
| **ui-agent** | Writes component unit tests; ensures components have test IDs |
| **state-agent** | Writes hook tests; mocks API via MSW; provides factory data |

---

## Delegation Examples

```python
# Write tests for Documents page
Agent(subagent_type="frontend-testing-agent", prompt="Write full test suite for Documents page: components, hooks, integration")

# Add MSW handlers for new endpoint
Agent(subagent_type="frontend-testing-agent", prompt="Add MSW handlers for /api/v1/reports/pdf and /api/v1/reports/excel")

# Create factories for new entity
Agent(subagent_type="frontend-testing-agent", prompt="Create factory for ScheduledReport entity with all variants")

# Audit accessibility
Agent(subagent_type="frontend-testing-agent", prompt="Run jest-axe on all Settings tab components and fix violations")

# Increase coverage
Agent(subagent_type="frontend-testing-agent", prompt="Add tests to reach 70% line coverage on hooks/useDocuments.ts")
```

---

*Specialized for testing. Provides MSW handlers, factories, test utilities to all agents. Writes tests for features implemented by pages-agent, ui-agent, state-agent.*