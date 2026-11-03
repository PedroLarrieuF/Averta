---
id: 38
title: "NF-e Rules Dashboard & Discrepancy Views"
priority: high
type: feature
agent: frontend
sprint: 3
estimate: L
status: ready
created: 2026-11-03
reviewed_by: techlead
dependencies: ["34", "35", "36"]
---

# Card #38: NF-e Rules Dashboard & Discrepancy Views

## Description
Build frontend components to display NF-e audit rules results, discrepancies, and validation details.

## Components to Build

### 1. NF-e Rules Dashboard Page
- **Route**: `/nfe/rules`
- **Features**: 
  - List all 18 NF-e rules (5 Critical, 7 High, 6 Medium)
  - Filter by priority (Critical/High/Medium)
  - Show rule status (implemented/pending)
  - Link to discrepancy details

### 2. NF-e Discrepancy Detail View
- **Route**: `/nfe/discrepancies/:id`
- **Features**:
  - Show NF-e XML data (chave de acesso, emitente, destinatário)
  - Display triggered rules with evidence
  - Show calculated vs declared values
  - Visual indicators for ICMS, FCP, DIFAL, CFOP validations

### 3. NF-e Validation Results Table
- **Component**: `NFEValidationTable`
- **Columns**: Rule Code, Rule Name, Priority, Status, Last Run, Discrepancies Count
- **Actions**: View details, Re-run validation, Export

### 4. NF-e Rule Configuration (Admin)
- **Route**: `/admin/nfe/rules`
- **Features**:
  - Enable/disable rules per company
  - Configure thresholds (tolerances)
  - Set custom cache TTL per rule

## Acceptance Criteria

### UI/UX
- [ ] Responsive design (mobile/tablet/desktop)
- [ ] Consistent with design system (Radix UI + Tailwind)
- [ ] Loading states and error handling
- [ ] Portuguese labels for all NF-e terms

### Integration
- [ ] Connect to backend `/api/v1/nfe/rules` endpoint (to be created)
- [ ] Connect to `/api/v1/nfe/discrepancies` endpoint
- [ ] TanStack Query for data fetching/caching
- [ ] Real-time updates via WebSocket (if available)

### Testing
- [ ] Component tests with Vitest + RTL
- [ ] E2E tests for critical flows
- [ ] Accessibility (WCAG AA)

## Technical Requirements

### New Files
- `frontend/src/pages/nfe/NFERulesDashboard.tsx`
- `frontend/src/pages/nfe/NFEDiscrepancyDetail.tsx`
- `frontend/src/components/nfe/NFEValidationTable.tsx`
- `frontend/src/components/nfe/NFERuleConfig.tsx`
- `frontend/src/hooks/useNFERules.ts`
- `frontend/src/types/nfe.ts`

### API Endpoints Needed (Backend)
- `GET /api/v1/nfe/rules` - List all NF-e rules with status
- `GET /api/v1/nfe/rules/:code` - Get rule details
- `GET /api/v1/nfe/discrepancies` - List discrepancies with filters
- `GET /api/v1/nfe/discrepancies/:id` - Get discrepancy detail
- `POST /api/v1/nfe/rules/:code/run` - Trigger rule execution
- `PATCH /api/v1/admin/nfe/rules/:code` - Update rule config

## Dependencies
- Card #34: NF-e Critical Rules (backend)
- Card #35: NF-e High Rules (backend)  
- Card #36: NF-e Medium Rules (backend)
- Card #15: Settings Pages (for admin config)

## Definition of Done
- [ ] All 4 components implemented and tested
- [ ] API integration working
- [ ] Component tests pass
- [ ] E2E tests for main flows
- [ ] Card moved to `review/`