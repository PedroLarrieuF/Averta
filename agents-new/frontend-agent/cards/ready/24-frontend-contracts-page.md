---
id: 24
title: "Contracts Page - CRUD + FreightTable Editor"
priority: high
type: feature
agent: frontend
sprint: 2
estimate: L
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #24: Contracts Page - CRUD + FreightTable Editor

## Description
Replace the `ComingSoon` placeholder in `frontend/src/pages/Contracts.tsx` with a complete Contracts management page featuring list, create, edit, detail, delete, and a **FreightTable editor** for managing freight rate tables with versioning.

## Acceptance Criteria

### List View
- [ ] Paginated, sortable table of contracts
- [ ] Columns: Number, Client, Carrier, Status, Vigência (Start/End), Success Fee %, Freight Tables Count, Created At
- [ ] Filters: search by number/client/carrier, status (ACTIVE/EXPIRED/PENDING), date range
- [ ] Actions per row: View, Edit, Delete (with confirmation), Manage Freight Tables
- [ ] "New Contract" button opens create modal

### Create/Edit Modal
- [ ] Form with React Hook Form + Zod validation
- [ ] Fields: Contract Number (required), Client (select, required), Carrier (select, required), Status (ACTIVE/EXPIRED/PENDING), Start Date (required), End Date, Success Fee % (required, decimal), Description
- [ ] Client/Carrier selects: fetch from `/api/v1/clients` and `/api/v1/carriers` (simple list)
- [ ] Date validation: end_date >= start_date
- [ ] Success Fee %: 0-100 with 2 decimals
- [ ] On submit: POST `/api/v1/contracts` (create) or PATCH `/api/v1/contracts/{id}` (edit)

### Detail View
- [ ] Contract info card with all fields
- [ ] Freight Tables section: list of FreightTable versions with actions: View, Edit, Create New Version, Set Active
- [ ] Related documents count, discrepancies count, contests count

### FreightTable Editor (Complex Feature)
- [ ] "Manage Freight Tables" opens dedicated view/modal
- [ ] List existing freight tables with version, status (DRAFT/ACTIVE/ARCHIVED), effective dates
- [ ] "New Version" creates draft copy of active table
- [ ] Editor: Grid/table for rates by:
  - Weight ranges (faixas de peso)
  - Cubage ranges (faixas de cubagem)
  - Distance ranges (faixas de distância)
  - Modal (Rodoviário, Aéreo, Marítimo, Ferroviário)
  - UF Origin/Destination
- [ ] Cell editing: inline edit with numeric input, validation
- [ ] Bulk operations: copy row, fill down, import CSV
- [ ] "Activate Version" sets status=ACTIVE, archives previous active
- [ ] Save draft / Publish (activate) actions

## Technical Requirements

### API Endpoints
```typescript
// Contracts
GET /api/v1/contracts?page&size&search&status
GET /api/v1/contracts/{id}
POST /api/v1/contracts
PATCH /api/v1/contracts/{id}
DELETE /api/v1/contracts/{id}

// Freight Tables
GET /api/v1/contracts/{contractId}/freight-tables
GET /api/v1/freight-tables/{id}
POST /api/v1/contracts/{contractId}/freight-tables
PATCH /api/v1/freight-tables/{id}
POST /api/v1/freight-tables/{id}/activate
DELETE /api/v1/freight-tables/{id}

// Reference data for selects
GET /api/v1/clients?status=ACTIVE&size=100
GET /api/v1/carriers?status=ACTIVE&size=100
```

### Components to Create
- `src/components/contracts/ContractsTable.tsx` - Main contracts table
- `src/components/contracts/ContractForm.tsx` - Create/Edit form
- `src/components/contracts/ContractDetailModal.tsx` - Detail with freight tables list
- `src/components/contracts/FreightTableEditor.tsx` - **Complex grid editor** (main component)
- `src/components/contracts/FreightTableGrid.tsx` - Editable grid component
- `src/components/contracts/FreightTableVersionManager.tsx` - Version list + activate
- `src/components/contracts/RateCellEditor.tsx` - Inline cell editor for rates

### Hooks to Create (delegate to state-agent)
- `useContracts(params)` - Paginated list
- `useContract(id)` - Single contract
- `useCreateContract()` - Create mutation
- `useUpdateContract()` - Update mutation
- `useDeleteContract()` - Delete mutation
- `useFreightTables(contractId)` - List freight tables
- `useFreightTable(id)` - Single freight table with full grid data
- `useCreateFreightTable()` - Create mutation
- `useUpdateFreightTable()` - Update mutation (grid data)
- `useActivateFreightTable()` - Activate mutation
- `useClientsSimple()` - Simple list for selects
- `useCarriersSimple()` - Simple list for selects

### Types Needed (delegate to state-agent)
```typescript
interface FreightTable {
  id: string;
  contract_id: string;
  version: number;
  status: 'DRAFT' | 'ACTIVE' | 'ARCHIVED';
  effective_from: string;
  effective_to: string | null;
  rates: FreightRate[]; // Grid data
}

interface FreightRate {
  id: string;
  weight_min: number | null;
  weight_max: number | null;
  cubage_min: number | null;
  cubage_max: number | null;
  distance_min: number | null;
  distance_max: number | null;
  modal: 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';
  uf_origin: string | null;
  uf_dest: string | null;
  rate_per_kg: number | null;
  rate_per_m3: number | null;
  rate_per_km: number | null;
  minimum_value: number | null;
}
```

## Dependencies
- Card #01: Testing infrastructure (DONE)
- Card #07: Design System (need advanced grid components)
- Card #22, #23: Clients/Carriers pages (for select data)
- Backend: Contracts + FreightTable endpoints already implemented

## Design References
- `frontend/src/index.css` - Tables, Forms, Modals, `.table-container`
- Consider using a grid library or build custom editable grid
- `frontend/src/components/Table.tsx` - Base table component
- `frontend/src/components/Modal.tsx` - Modal wrapper

## Testing Requirements
- Unit tests for ContractForm validation
- Unit tests for FreightTableGrid editing logic
- Integration tests for CRUD flows
- MSW handlers for all contract/freight-table endpoints
- Accessibility tests

## Definition of Done
- [ ] Contracts list page works with pagination, filters
- [ ] Contract CRUD works
- [ ] FreightTable list shows versions with status
- [ ] FreightTable Editor: grid renders, inline edit works
- [ ] Version management: create draft, activate, archive works
- [ ] CSV import/export for freight tables (bonus)
- [ ] All quality gates pass: `pnpm lint && pnpm build && pnpm test`
- [ ] Tests written and passing
- [ ] Card moved to `review/`

## Notes
- **Most complex frontend card** - FreightTable editor is a spreadsheet-like grid
- Backend contracts/freight-table endpoints are already implemented per `backend/README.md`
- Consider using `@tanstack/react-table` for the editable grid (already in deps or add)
- Freight table versioning: only one ACTIVE per contract at a time
- Rate cells: support multiple rate types (per kg, per m3, per km, minimum)
- Validation: rates must be positive numbers, ranges must not overlap