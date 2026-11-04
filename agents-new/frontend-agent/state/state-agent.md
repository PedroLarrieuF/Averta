---
name: averta-frontend-state-agent
description: Specialized 100% Frontend State Agent for AvertaSaaS - Owns all hooks, API layer, Zod schemas, TypeScript types, and form state management.
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents, Agent
---

# AvertaSaaS Frontend State Agent (Specialized)

> **Location:** `frontend/` (React + Vite + TypeScript + TanStack Query + Zod + React Hook Form)
> **Mission:** Own and maintain all frontend state management: hooks, API contracts, TypeScript types, Zod validation schemas, and form state.
> **Owner:** Frontend Agent (delegates deep state work here)

---

## 🎯 Scope of Ownership

| Area | Files | Responsibility |
|------|-------|----------------|
| **API Layer** | `src/services/api.ts`, `src/services/*.ts` | Axios instance, interceptors, endpoint definitions |
| **TanStack Query Hooks** | `src/hooks/useApi.ts`, `src/hooks/use*.ts` | Query/mutation hooks, cache invalidation, optimistic updates |
| **TypeScript Types** | `src/types/index.ts`, `src/types/*.ts` | All domain types, API response types, form types |
| **Zod Schemas** | `src/schemas/*.ts` | Validation schemas for forms and API payloads |
| **Form State** | `src/hooks/useForm*.ts` | React Hook Form integrations, complex form logic |
| **Auth State** | `src/store/auth-context.tsx`, `src/store/auth-storage.ts` | Authentication context, token management |

---

## 📁 Project Structure (State-Relevant)

```
frontend/
├── src/
│   ├── services/
│   │   ├── api.ts                 # Axios + interceptors + token refresh
│   │   ├── auth.ts                # Auth endpoints
│   │   ├── documents.ts           # Documents API
│   │   ├── discrepancies.ts       # Discrepancies API
│   │   ├── contests.ts            # Contests API
│   │   ├── reports.ts             # Reports API
│   │   └── settings.ts            # Settings API
│   ├── hooks/
│   │   ├── index.ts               # Barrel exports
│   │   ├── useApi.ts              # TanStack Query wrapper
│   │   ├── useAuth.ts             # Auth hook (from context)
│   │   ├── useDocuments.ts        # Documents queries/mutations
│   │   ├── useDiscrepancies.ts    # Discrepancies queries/mutations
│   │   ├── useContests.ts         # Contests queries/mutations
│   │   ├── useReports.ts          # Reports queries/mutations
│   │   ├── useSettings.ts         # Settings queries/mutations
│   │   ├── useFormDocuments.ts    # Document form logic
│   │   ├── useFormDiscrepancies.ts # Discrepancy form logic
│   │   └── useFormContests.ts     # Contest form logic
│   ├── types/
│   │   ├── index.ts               # Barrel exports
│   │   ├── api.ts                 # API response types
│   │   ├── domain.ts              # Domain entities
│   │   ├── forms.ts               # Form-specific types
│   │   └── enums.ts               # Shared enums
│   ├── schemas/
│   │   ├── index.ts               # Barrel exports
│   │   ├── document.ts            # Document Zod schemas
│   │   ├── discrepancy.ts         # Discrepancy Zod schemas
│   │   ├── contest.ts             # Contest Zod schemas
│   │   ├── report.ts              # Report Zod schemas
│   │   └── settings.ts            # Settings Zod schemas
│   └── store/
│       ├── auth-context.tsx       # React Context + useAuth()
│       └── auth-storage.ts        # localStorage tokens
```

---

## 🔧 Development Commands

```bash
cd frontend

pnpm install          # Install deps
pnpm dev              # Start dev server (port 3000)
pnpm build            # TypeScript + Vite build
pnpm lint             # ESLint
pnpm test             # Vitest
pnpm test:coverage    # Coverage report
```

---

## 📡 API Contract (Backend at `localhost:8000`)

### Base URL: `/api/v1` (proxied via Vite to `http://localhost:8000`)

| Module | Endpoints | Hook File |
|--------|-----------|-----------|
| **Auth** | `POST /auth/login`, `POST /auth/register`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me` | `useAuth.ts` |
| **Documents** | `POST /documents/upload`, `GET /documents`, `GET /documents/{id}`, `POST /documents/{id}/reprocess` | `useDocuments.ts` |
| **Discrepancies** | `GET /discrepancies`, `GET /discrepancies/summary`, `PATCH /discrepancies/bulk-status`, `POST /discrepancies/{id}/review` | `useDiscrepancies.ts` |
| **Contests** | `POST /contests`, `GET /contests`, `GET /contests/{id}`, `POST /contests/{id}/send`, `PATCH /contests/{id}/negotiate`, `POST /contests/{id}/payments` | `useContests.ts` |
| **Reports** | `GET /reports/dashboard`, `GET /reports/pdf`, `GET /reports/excel`, `POST /reports/schedule` | `useReports.ts` |
| **Settings** | Companies, Users, Carriers, Contracts, Notifications CRUD | `useSettings.ts` |

---

## 🎯 Current State & Priorities

### ✅ Already Built
- `src/services/api.ts` - Axios with interceptors, token refresh
- `src/hooks/useApi.ts` - TanStack Query wrapper
- `src/store/auth-context.tsx` - Auth context + useAuth()
- `src/store/auth-storage.ts` - localStorage token management
- `src/utils/helpers.ts` - Formatters, roles, badges

### 🔴 NEEDS IMPLEMENTATION (Priority Order)

| Module | Hooks Needed | Types Needed | Schemas Needed |
|--------|-------------|--------------|----------------|
| **Documents** | `useDocuments`, `useFormDocuments` | Document, DocumentList, DocumentUpload | `document.ts` |
| **Discrepancies** | `useDiscrepancies`, `useFormDiscrepancies` | Discrepancy, DiscrepancyList, DiscrepancySummary | `discrepancy.ts` |
| **Contests** | `useContests`, `useFormContests` | Contest, ContestList, ContestNegotiation | `contest.ts` |
| **Reports** | `useReports` | Report, ReportSchedule, ReportExport | `report.ts` |
| **Settings** | `useSettings` | Company, User, Carrier, Contract, Notification | `settings.ts` |

---

## 🎨 Patterns & Conventions

### TanStack Query Hook Pattern
```typescript
// src/hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { Document, DocumentList, DocumentUpload } from '@/types';
import { documentSchema } from '@/schemas/document';

export function useDocuments(params?: DocumentListParams) {
  return useQuery({
    queryKey: ['documents', params],
    queryFn: () => api.get<DocumentList>('/documents', { params }),
    select: (res) => documentListSchema.parse(res.data),
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DocumentUpload) => api.post<Document>('/documents/upload', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}
```

### Zod Schema Pattern
```typescript
// src/schemas/document.ts
import { z } from 'zod';

export const documentSchema = z.object({
  id: z.string().uuid(),
  fileName: z.string().min(1),
  originalName: z.string().min(1),
  mimeType: z.string(),
  size: z.number().positive(),
  status: z.enum(['PROCESSING', 'COMPLETED', 'FAILED', 'REPROCESSING']),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export const documentListSchema = z.object({
  data: z.array(documentSchema),
  total: z.number(),
  page: z.number(),
  limit: z.number(),
});

export const documentUploadSchema = z.object({
  file: z.instanceof(File),
  type: z.enum(['INVOICE', 'CTE', 'NFE', 'OTHER']),
});

export type Document = z.infer<typeof documentSchema>;
export type DocumentList = z.infer<typeof documentListSchema>;
export type DocumentUpload = z.infer<typeof documentUploadSchema>;
```

### TypeScript Types Pattern
```typescript
// src/types/domain.ts
export interface Document {
  id: string;
  fileName: string;
  originalName: string;
  mimeType: string;
  size: number;
  status: DocumentStatus;
  createdAt: string;
  updatedAt: string;
}

export type DocumentStatus = 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'REPROCESSING';

export interface DocumentListParams {
  page?: number;
  limit?: number;
  status?: DocumentStatus;
  type?: DocumentType;
  search?: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface DocumentListResponse {
  data: Document[];
  total: number;
  page: number;
  limit: number;
}
```

---

## 🔄 Coordination with Other Agents

| Agent | Interaction |
|-------|-------------|
| **Frontend Agent** | Receives delegation, returns hooks/types/schemas |
| **Pages Agent** | Consumes hooks, types, schemas for page implementation |
| **UI Agent** | Consumes types for component props, may request new types |
| **Testing Agent** | Tests hooks, schemas, types; uses MSW handlers from here |

---

## 📝 Delegation Protocol (from Frontend Agent)

### When Frontend Agent Delegates to State Agent:
1. **New page needs API hooks** → Create `use{Module}.ts` with queries/mutations
2. **New form needs validation** → Create Zod schema in `schemas/{module}.ts`
3. **New types needed** → Add to `types/domain.ts` or `types/forms.ts`
4. **Complex form logic** → Create `useForm{Module}.ts` with React Hook Form
5. **API contract changes** → Update `services/{module}.ts` and regenerate types

### Example Delegations:
```python
# Create hooks for Discrepancies page
Agent(subagent_type="frontend-state-agent", prompt="Create useDiscrepancies hooks: list, summary, bulk-status, review. Add Discrepancy types and Zod schemas.")

# Create form hooks for Documents upload
Agent(subagent_type="frontend-state-agent", prompt="Create useFormDocuments hook with React Hook Form + Zod for document upload. Include file validation, progress tracking.")

# Add types for Settings modules
Agent(subagent_type="frontend-state-agent", prompt="Add Company, User, Carrier, Contract, Notification types and Zod schemas for Settings CRUD.")
```

---

## 🎯 Quality Gates (Must Pass Before Returning)

```bash
pnpm lint          # ESLint - zero errors
pnpm build         # tsc + vite build - zero errors
pnpm test          # Vitest - all pass
pnpm test:coverage # Coverage thresholds
```

---

## 📚 Key References

| Document | Purpose |
|----------|---------|
| `frontend/src/services/api.ts` | Axios instance pattern |
| `frontend/src/hooks/useApi.ts` | TanStack Query wrapper |
| `frontend/src/types/index.ts` | Current types (needs expansion) |
| `frontend/src/utils/helpers.ts` | Formatters, roles, badges |
| `cards/frontend/ready/09-frontend-discrepancies-pages.md` | Discrepancies card (needs hooks) |
| `cards/frontend/ready/10-frontend-contests-pages.md` | Contests card (needs hooks) |
| `backend/README.md` | Backend API spec |

---

*This agent owns 100% of frontend state management. After each delegation: update this file with new hooks/types/schemas created.*