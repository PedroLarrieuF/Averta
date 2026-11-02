---
id: 23
title: "Carriers Page - CRUD"
priority: high
type: feature
agent: frontend
sprint: 2
estimate: M
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #23: Carriers Page - CRUD

## Description
Replace the `ComingSoon` placeholder in `frontend/src/pages/Carriers.tsx` with a complete Carriers management page featuring list, create, edit, detail, and delete functionality.

## Acceptance Criteria

### List View
- [ ] Paginated, sortable table of carriers
- [ ] Columns: Name, Document (CNPJ), Email, Phone, ANTT Registry, Status, Branches Count, Created At
- [ ] Filters: search by name/document, status (ACTIVE/INACTIVE), has ANTT
- [ ] Actions per row: View, Edit, Delete (with confirmation)
- [ ] "New Carrier" button opens create modal

### Create/Edit Modal
- [ ] Form with React Hook Form + Zod validation
- [ ] Fields: Name (required), Document (CNPJ, required, validated), Email, Phone, ANTT Registry Number, Address (street, number, complement, neighborhood, city, state, zip), Status (ACTIVE/INACTIVE)
- [ ] CNPJ format validation (Brazilian format)
- [ ] ANTT registry format validation
- [ ] Duplicate document check (show error if exists)
- [ ] On submit: POST `/api/v1/carriers` (create) or PATCH `/api/v1/carriers/{id}` (edit)

### Detail View (Modal or Page)
- [ ] Carrier info card with ANTT registry display
- [ ] Branches table (Branch list) with actions: View, Edit, Delete, New Branch
- [ ] Related contracts count, documents count, discrepancies count

### Branch Management (Nested)
- [ ] "New Branch" modal: Name, Code, Address, Is Main (boolean), ANTT Code (optional)
- [ ] Branch CRUD similar to carrier

## Technical Requirements

### API Endpoints
```typescript
// Already available in backend
GET /api/v1/carriers?page&size&search&status
GET /api/v1/carriers/{id}
POST /api/v1/carriers
PATCH /api/v1/carriers/{id}
DELETE /api/v1/carriers/{id}

// Branches
GET /api/v1/carriers/{carrierId}/branches
POST /api/v1/carriers/{carrierId}/branches
PATCH /api/v1/branches/{id}
DELETE /api/v1/branches/{id}
```

### Components to Create
- `src/components/carriers/CarriersTable.tsx` - Table with pagination, sorting, filters
- `src/components/carriers/CarrierForm.tsx` - Create/Edit form (shared)
- `src/components/carriers/CarrierDetailModal.tsx` - Detail view with branches
- `src/components/carriers/BranchForm.tsx` - Branch create/edit form (can reuse from clients)
- `src/components/carriers/BranchesTable.tsx` - Branches table in detail modal

### Hooks to Create (delegate to state-agent)
- `useCarriers(params)` - TanStack Query for paginated list
- `useCarrier(id)` - Single carrier fetch
- `useCreateCarrier()` - Create mutation
- `useUpdateCarrier()` - Update mutation
- `useDeleteCarrier()` - Delete mutation
- `useCarrierBranches(carrierId)` - Branches list
- `useCreateBranch()` - Branch create mutation
- `useUpdateBranch()` - Branch update mutation
- `useDeleteBranch()` - Branch delete mutation

### Zod Schemas (delegate to state-agent)
```typescript
const carrierSchema = z.object({
  name: z.string().min(2, "Nome deve ter pelo menos 2 caracteres"),
  document: z.string().refine(validCNPJ, "CNPJ inválido"),
  email: z.string().email("Email inválido").optional().or(z.literal("")),
  phone: z.string().optional(),
  antt_registry: z.string().optional(), // ANTT format validation
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
  antt_code: z.string().optional(),
});
```

## Dependencies
- Card #01: Testing infrastructure (DONE)
- Card #07: Design System (Modal, Form components - mostly done)
- Card #22: Clients Page (similar structure, can reuse patterns)
- Backend: Carriers endpoints already implemented

## Design References
- `frontend/src/index.css` - Tables, Forms, Modals
- `frontend/src/components/Modal.tsx` - Use existing Modal component
- `frontend/src/components/Table.tsx` - Use existing Table component
- `frontend/src/utils/helpers.ts` - `formatCurrency`, `formatDate`, `getStatusBadge`

## Testing Requirements
- Unit tests for CarrierForm validation (CNPJ, ANTT)
- Integration tests for CRUD flows
- MSW handlers for all carrier/branch endpoints
- Accessibility tests

## Definition of Done
- [ ] List page renders with pagination, sorting, filters
- [ ] Create modal works with validation (CNPJ, ANTT)
- [ ] Edit modal pre-fills and updates correctly
- [ ] Delete works with confirmation
- [ ] Branch management works
- [ ] All quality gates pass: `pnpm lint && pnpm build && pnpm test`
- [ ] Tests written and passing
- [ ] Card moved to `review/`

## Notes
- Backend carriers endpoints are already implemented per `backend/README.md`
- Very similar to Clients page - reuse components/patterns where possible
- ANTT registry validation: implement helper for Brazilian ANTT format
- Status badge: use `getStatusBadge(status)` from helpers
- Consider creating shared `BranchForm` and `BranchesTable` components