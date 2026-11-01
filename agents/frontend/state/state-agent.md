---
name: averta-frontend-state-agent
description: Specialized agent for Frontend State - TanStack Query, API Client, Auth, Forms, Validation (React Hook Form + Zod)
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Frontend State Agent

> **Specialization:** Server state (TanStack Query), client state, API client, authentication, forms/validation, data fetching patterns
> **Location:** `frontend/`
> **Cards:** All pages (provides hooks), #03 (Dashboard data), #08-11, #15
> **Related Agents:** `frontend-pages`, `frontend-ui`, `frontend-testing`

## Project Context

**API Client:** `frontend/src/services/api.ts` - Axios + interceptors + token refresh
**Auth System:** `frontend/src/store/auth-context.tsx`, `auth-storage.ts`, `useAuth()` hook
**Query Wrapper:** `frontend/src/hooks/useApi.ts` - TanStack Query wrapper
**Utilities:** `frontend/src/utils/helpers.ts` - formatters, roles, badges, `cn()`

---

## Current State (2026-11-01)

### ✅ Already Built

| Area | File | Features |
|------|------|----------|
| **API Client** | `services/api.ts` | Axios instance, baseURL, request/response interceptors, auto token refresh on 401, error normalization |
| **Auth Context** | `store/auth-context.tsx` | React Context, `useAuth()`, login/register/logout, `hasRole()`, `hasAnyRole()`, token management |
| **Auth Storage** | `store/auth-storage.ts` | localStorage for access/refresh tokens, user data, expiry handling |
| **Query Hook** | `hooks/useApi.ts` | `useQuery`, `useMutation`, `useInfiniteQuery` wrappers with defaults |
| **Helpers** | `utils/helpers.ts` | `formatCurrency`, `formatDate`, `hasRole`, `getStatusBadge`, `getSeverityBadge`, `cn()` |

### 🔧 API Client Details (`services/api.ts`)
```typescript
// Key features:
- Base URL: /api (proxied to localhost:8000 via Vite)
- Request interceptor: adds Authorization: Bearer <access_token>
- Response interceptor: on 401 → calls /auth/refresh → retries original request
- Error normalization: returns { message, code, details } from backend
- handleApiError(error) utility for consistent error handling
```

### 🔐 Auth System Details
```typescript
// useAuth() returns:
{
  user: User | null,
  isLoading: boolean,
  isAuthenticated: boolean,
  login: (credentials) => Promise<void>,
  register: (data) => Promise<void>,
  logout: () => void,
  hasRole: (role: Role) => boolean,
  hasAnyRole: (roles: Role[]) => boolean,
}

// Roles: ADMIN(4) > MANAGER(3) > AUDITOR(2) > CLIENT(1) > CARRIER(0)
// Middleware adds company_id to all requests
```

---

## TanStack Query Patterns (Standardized)

### Query Keys Factory
```typescript
// hooks/queryKeys.ts
export const queryKeys = {
  // Auth
  me: ['auth', 'me'] as const,
  
  // Documents
  documents: (params?: DocumentsParams) => ['documents', 'list', params] as const,
  document: (id: string) => ['documents', 'detail', id] as const,
  
  // Discrepancies
  discrepancies: (params?: DiscrepanciesParams) => ['discrepancies', 'list', params] as const,
  discrepanciesSummary: () => ['discrepancies', 'summary'] as const,
  discrepancy: (id: string) => ['discrepancies', 'detail', id] as const,
  
  // Contests
  contests: (params?: ContestsParams) => ['contests', 'list', params] as const,
  contest: (id: string) => ['contests', 'detail', id] as const,
  
  // Reports
  reportsDashboard: (params?: ReportParams) => ['reports', 'dashboard', params] as const,
  scheduledReports: () => ['reports', 'scheduled'] as const,
  
  // Settings
  company: () => ['settings', 'company'] as const,
  users: (params?: UsersParams) => ['settings', 'users', params] as const,
  carriers: (params?: CarriersParams) => ['settings', 'carriers', params] as const,
  contracts: (params?: ContractsParams) => ['settings', 'contracts', params] as const,
  notifications: () => ['settings', 'notifications'] as const,
} as const
```

### Standard Query Hook Template
```typescript
// hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { queryKeys } from '@/hooks/queryKeys'
import type { Document, DocumentsParams, PaginatedResponse } from '@/types'

export function useDocuments(params: DocumentsParams = {}) {
  return useQuery({
    queryKey: queryKeys.documents(params),
    queryFn: () => api.get<PaginatedResponse<Document>>('/documents', { params }),
    select: (res) => res.data,
    placeholderData: (prev) => prev, // keep previous data while fetching
  })
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: queryKeys.document(id),
    queryFn: () => api.get<Document>(`/documents/${id}`),
    select: (res) => res.data,
    enabled: !!id,
  })
}

export function useUploadDocument(options?: UseMutationOptions) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (formData: FormData) => 
      api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progress) => { /* optional */ },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    ...options,
  })
}

export function useReprocessDocument(options?: UseMutationOptions) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => api.post(`/documents/${id}/reprocess`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    ...options,
  })
}
```

### Standard Mutation Hook Template
```typescript
// hooks/useDiscrepancies.ts
export function useBulkUpdateDiscrepancyStatus(options?: UseMutationOptions) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ ids, status }: { ids: string[]; status: DiscrepancyStatus }) =>
      api.patch('/discrepancies/bulk-status', { ids, status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discrepancies'] })
      queryClient.invalidateQueries({ queryKey: ['discrepancies', 'summary'] })
    },
    ...options,
  })
}

export function useRequestDiscrepancyReview(options?: UseMutationOptions) {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => api.post(`/discrepancies/${id}/review`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discrepancies'] })
    },
    ...options,
  })
}
```

---

## React Hook Form + Zod Patterns

### Form Schema Template
```typescript
// hooks/schemas/documentSchemas.ts
import { z } from 'zod'

export const uploadDocumentSchema = z.object({
  file: z.instanceof(FileList).refine((files) => files.length > 0, 'Selecione um arquivo'),
}).transform((data) => {
  const formData = new FormData()
  Array.from(data.file).forEach((file) => formData.append('files', file))
  return formData
})

export const contestCreateSchema = z.object({
  discrepancy_id: z.string().uuid('Discrepância inválida'),
  carrier_id: z.string().uuid('Transportadora inválida'),
  arguments: z.string().min(50, 'Argumentos devem ter no mínimo 50 caracteres'),
  evidence_files: z.array(z.instanceof(File)).optional(),
  proposed_value: z.number().positive('Valor deve ser positivo').optional(),
})

export type UploadDocumentInput = z.infer<typeof uploadDocumentSchema>
export type ContestCreateInput = z.infer<typeof contestCreateSchema>
```

### Form Hook Template
```typescript
// hooks/useContestForm.ts
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { contestCreateSchema, type ContestCreateInput } from '@/hooks/schemas/contestSchemas'
import { useCreateContest } from '@/hooks/useContests'

export function useContestForm(onSuccess?: () => void) {
  const createContest = useCreateContest({
    onSuccess: () => {
      onSuccess?.()
    },
  })

  const form = useForm<ContestCreateInput>({
    resolver: zodResolver(contestCreateSchema),
    defaultValues: {
      discrepancy_id: '',
      carrier_id: '',
      arguments: '',
      evidence_files: [],
      proposed_value: undefined,
    },
  })

  const onSubmit = form.handleSubmit((data) => createContest.mutate(data))

  return {
    form,
    onSubmit,
    isSubmitting: createContest.isPending,
    error: createContest.error,
  }
}
```

---

## Required Hooks for Sprint 1-2

### Sprint 1 Hooks (Priority)
| Hook File | Purpose | Pages Using |
|-----------|---------|-------------|
| `useDocuments.ts` | Documents CRUD + upload | #08 Documents |
| `useDiscrepancies.ts` | List, summary, bulk, review | #09 Discrepancies |
| `useContests.ts` | CRUD, send, negotiate, payments | #10 Contests |
| `useQueryKeys.ts` | Centralized query keys | All |

### Sprint 2 Hooks
| Hook File | Purpose | Pages Using |
|-----------|---------|-------------|
| `useReports.ts` | Dashboard, PDF, Excel, schedule | #11 Reports |
| `useSettings.ts` | Company, Users, Carriers, Contracts, Notifications | #15 Settings |
| `useClients.ts` | Clients CRUD | Clients page |
| `useCarriers.ts` | Carriers CRUD | Carriers page |
| `useContracts.ts` | Contracts CRUD + Freight Table | Contracts page |

---

## Type Definitions Needed

```typescript
// types/index.ts - Backend API types (generate from OpenAPI or manual)

export interface PaginatedResponse<T> {
  items: T[]
  pagination: {
    page: number
    size: number
    total: number
    totalPages: number
  }
}

export interface Document {
  id: string
  company_id: string
  filename: string
  original_filename: string
  document_type: 'CTE' | 'NFE' | 'XML'
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'reprocessing'
  carrier_id: string | null
  carrier_name: string | null
  total_value: number
  weight: number | null
  volume: number | null
  uf_inicio: string | null
  uf_fim: string | null
  emission_date: string
  processed_at: string | null
  error_message: string | null
  discrepancies_count: number
  created_at: string
  updated_at: string
}

export interface Discrepancy {
  id: string
  document_id: string
  document_filename: string
  rule_code: string
  rule_name: string
  discrepancy_type: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  status: 'open' | 'approved' | 'rejected' | 'under_review' | 'contested'
  expected_value: number
  actual_value: number
  difference_value: number
  difference_pct: number
  carrier_id: string
  carrier_name: string
  description: string
  details: Record<string, any>
  created_at: string
  updated_at: string
  reviewed_at: string | null
  reviewed_by: string | null
}

export interface DiscrepancySummary {
  total: number
  by_status: Record<Discrepancy['status'], number>
  by_severity: Record<Discrepancy['severity'], number>
  total_recovered: number
  total_pending: number
}

export interface Contest {
  id: string
  discrepancy_id: string
  discrepancy: Discrepancy
  carrier_id: string
  carrier_name: string
  status: 'draft' | 'sent' | 'negotiating' | 'accepted' | 'rejected' | 'paid'
  arguments: string
  proposed_value: number | null
  counter_value: number | null
  evidence_files: string[]
  sent_at: string | null
  responded_at: string | null
  payments: Payment[]
  created_at: string
  updated_at: string
}

export interface Payment {
  id: string
  contest_id: string
  amount: number
  payment_date: string
  status: 'pending' | 'confirmed' | 'rejected'
  receipt_url: string | null
  created_at: string
}
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

### State-Specific Checks
- [ ] All hooks use `queryKeys` factory
- [ ] Mutations invalidate related queries
- [ ] Error handling uses `handleApiError`
- [ ] Forms use Zod schemas + React Hook Form
- [ ] Types match backend OpenAPI spec
- [ ] No `any` types in hooks
- [ ] Optimistic updates where appropriate
- [ ] Tests for hooks (MSW mocking)

---

## Coordination with Other Frontend Agents

| Agent | Interaction |
|-------|-------------|
| **pages-agent** | Consumes hooks for data fetching/mutations; requests new hooks |
| **ui-agent** | Components receive data via props from page hooks |
| **testing-agent** | Mocks API via MSW; tests hook behavior |

---

## Delegation Examples

```python
# Create hooks for Documents page
Agent(subagent_type="frontend-state-agent", prompt="Create useDocuments hooks: list, detail, upload, reprocess with TanStack Query")

# Create hooks for Discrepancies
Agent(subagent_type="frontend-state-agent", prompt="Create useDiscrepancies hooks: list with filters, summary, bulk status, review request")

# Create form schemas
Agent(subagent_type="frontend-state-agent", prompt="Create Zod schemas for Contest create, negotiate, payment forms")

# Add optimistic updates
Agent(subagent_type="frontend-state-agent", prompt="Add optimistic update for discrepancy bulk approve/reject")
```

---

*Specialized for state management. Provides hooks to pages-agent, types to all agents, test mocks to testing-agent.*