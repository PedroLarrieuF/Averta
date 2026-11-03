---
id: 22
title: "Clients Page - CRUD"
priority: high
type: feature
agent: frontend
sprint: 2
estimate: M
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #22: Clients Page - CRUD

## Description
Replace the `ComingSoon` placeholder in `frontend/src/pages/Clients.tsx` with a complete Clients management page featuring list, create, edit, detail, and delete functionality.

## Acceptance Criteria

### List View
- [ ] Paginated, sortable table of clients
- [ ] Columns: Name, Document (CNPJ/CPF), Email, Status, Branches Count, Created At
- [ ] Filters: search by name/document, status (ACTIVE/INACTIVE), date range
- [ ] Actions per row: View, Edit, Delete (with confirmation)
- [ ] "New Client" button opens create modal

### Create/Edit Modal
- [ ] Form with React Hook Form + Zod validation
- [ ] Fields: Name (required), Document (CNPJ/CPF, required, validated), Email, Phone, Address (street, number, complement, neighborhood, city, state, zip), Status (ACTIVE/INACTIVE)
- [ ] CNPJ/CPF format validation (Brazilian format)
- [ ] Duplicate document check (show error if exists)
- [ ] On submit: POST `/api/v1/clients` (create) or PATCH `/api/v1/clients/{id}` (edit)

### Detail View (Modal or Page)
- [ ] Client info card
- [ ] Branches table (ClientBranch list) with actions: View, Edit, Delete, New Branch
- [ ] Related documents count, discrepancies count

### Branch Management (Nested)
- [ ] "New Branch" modal: Name, Code, Address, Is Main (boolean)
- [ ] Branch CRUD similar to client

## Technical Requirements

### API Endpoints
```typescript
// Already available in backend
GET /api/v1/clients?page&size&search&status
GET /api/v1/clients/{id}
POST /api/v1/clients
PATCH /api/v1/clients/{id}
DELETE /api/v1/clients/{id}

// Branches
GET /api/v1/clients/{clientId}/branches
POST /api/v1/clients/{clientId}/branches
PATCH /api/v1/branches/{id}
DELETE /api/v1/branches/{id}
```

### Components to Create
- `src/components/clients/ClientsTable.tsx` - Table with pagination, sorting, filters
- `src/components/clients/ClientForm.tsx` - Create/Edit form (shared)
- `src/components/clients/ClientDetailModal.tsx` - Detail view with branches
- `src/components/clients/BranchForm.tsx` - Branch create/edit form
- `src/components/clients/BranchesTable.tsx` - Branches table in detail modal

### Hooks to Create (delegate to state-agent)
- `useClients(params)` - TanStack Query for paginated list
- `useClient(id)` - Single client fetch
- `useCreateClient()` - Create mutation
- `useUpdateClient()` - Update mutation
- `useDeleteClient()` - Delete mutation
- `useClientBranches(clientId)` - Branches list
- `useCreateBranch()` - Branch create mutation
- `useUpdateBranch()` - Branch update mutation
- `useDeleteBranch()` - Branch delete mutation

### Zod Schemas (delegate to state-agent)
```typescript
const clientSchema = z.object({
  name: z.string().min(2, "Nome deve ter pelo menos 2 caracteres"),
  document: z.string().refine(validCNPJorCPF, "CNPJ/CPF inválido"),
  email: z.string().email("Email inválido").optional().or(z.literal("")),
  phone: z.string().optional(),
  address: z.object({
    street: z.string().optional(),
    number: z.string().optional(),
    complement: z.string().optional(),
    neighborhood: z.string().optional(),
    city: z.string().optional(),
    state: z.string().length(2, "UF deve ter 2 caracteres").optional(),
    zip: z.string().optional(),
  }).optional(),
  status: z.enum(["ACTIVE", "INACTIVE"]),
});

const branchSchema = z.object({
  name: z.string().min(2),
  code: z.string().min(1),
  address: z.object({...}).optional(),
  is_main: z.boolean(),
});
```

## Dependencies
- Card #01: Testing infrastructure (DONE)
- Card #07: Design System (need Modal, Form components - mostly done)
- Backend: Clients endpoints already implemented

## Design References
- `frontend/src/index.css` - Tables: `.table-container`, `.table`, `.table th`, `.table td`
- `frontend/src/components/Modal.tsx` - Use existing Modal component
- `frontend/src/components/Table.tsx` - Use existing Table component
- `frontend/src/utils/helpers.ts` - `formatCurrency`, `formatDate`, `getStatusBadge`

## Testing Requirements
- Unit tests for ClientForm validation
- Integration tests for CRUD flows
- MSW handlers for all client/branch endpoints
- Accessibility tests

## Definition of Done
- [ ] List page renders with pagination, sorting, filters
- [ ] Create modal works with validation
- [ ] Edit modal pre-fills and updates correctly
- [ ] Delete works with confirmation
- [ ] Branch management works
- [ ] All quality gates pass: `pnpm lint && pnpm build && pnpm test`
- [ ] Tests written and passing
- [ ] Card moved to `review/`

## Notes
- Backend clients endpoints are already implemented per `backend/README.md`
- Use `cn()` from `utils/helpers.ts` for class merging
- Document validation: implement `validCNPJorCPF` helper (can reuse from backend logic)
- Status badge: use `getStatusBadge(status)` from helpers