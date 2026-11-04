---
id: 27
title: "TypeScript Types Barrel Exports"
priority: low
type: tech-debt
agent: frontend
sprint: 3
estimate: S
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #27: TypeScript Types Barrel Exports

## Description
Complete the `frontend/src/types/index.ts` barrel export file with all TypeScript types used across the frontend application. Currently the file exists but is empty/minimal.

## Current State
- `frontend/src/types/index.ts` exists but has minimal exports
- Types are defined inline in components/hooks/pages
- No centralized type definitions
- Causes duplication and inconsistency

## Acceptance Criteria

### Centralized Type Definitions
- [ ] Create type definitions for all API responses
- [ ] Create type definitions for all form schemas
- [ ] Create type definitions for all UI state
- [ ] Export all types from `frontend/src/types/index.ts`
- [ ] Update all files to import from `@/types` (or `../types`)

### Required Type Categories

#### 1. API Response Types (from backend OpenAPI)
```typescript
// Auth
interface User { id: string; name: string; email: string; role: UserRole; company_id: string; status: UserStatus; created_at: string; }
interface LoginResponse { access_token: string; refresh_token: string; token_type: string; user: User; }

// Documents
interface Document { id: string; company_id: string; filename: string; status: DocumentStatus; document_type: DocumentType; parsed_data: ParsedDocumentData | null; created_at: string; }
interface ParsedDocumentData { /* 40+ fields from xml_parser */ }
interface DocumentListResponse { data: Document[]; total: number; page: number; size: number; }

// Discrepancies
interface Discrepancy { id: string; document_id: string; rule_code: string; severity: DiscrepancySeverity; status: DiscrepancyStatus; description: string; expected_value: number | null; actual_value: number | null; difference_pct: number | null; created_at: string; }
interface DiscrepancySummary { by_status: Record<DiscrepancyStatus, number>; by_severity: Record<DiscrepancySeverity, number>; by_rule: Record<string, number>; total: number; }
interface DiscrepancyListResponse { data: Discrepancy[]; total: number; page: number; size: number; }

// Contests
interface Contest { id: string; company_id: string; status: ContestStatus; carrier_id: string; total_amount: number; success_fee: number; net_recovery: number; created_at: string; }
interface ContestItem { id: string; contest_id: string; discrepancy_id: string; status: ContestItemStatus; }
interface ContestListResponse { data: Contest[]; total: number; page: number; size: number; }

// Reports
interface ReportsDashboardResponse { /* from Card #21 */ }
interface ScheduledReport { /* from Card #21 */ }

// Settings
interface Client { /* from Card #22 */ }
interface ClientBranch { /* from Card #22 */ }
interface Carrier { /* from Card #23 */ }
interface Branch { /* from Card #23 */ }
interface Contract { /* from Card #24 */ }
interface FreightTable { /* from Card #24 */ }
interface FreightRate { /* from Card #24 */ }

// Notifications
interface Notification { id: string; type: NotificationType; channel: NotificationChannel; title: string; message: string; read: boolean; created_at: string; }
interface NotificationPreferences { email_enabled: boolean; in_app_enabled: boolean; weekly_report: boolean; discrepancy_alerts: boolean; contest_updates: boolean; }
```

#### 2. Form Types (Zod Inferred)
```typescript
// From each form schema
type LoginForm = z.infer<typeof loginSchema>;
type RegisterForm = z.infer<typeof registerSchema>;
type ClientForm = z.infer<typeof clientSchema>;
type CarrierForm = z.infer<typeof carrierSchema>;
type ContractForm = z.infer<typeof contractSchema>;
type BranchForm = z.infer<typeof branchSchema>;
type FreightTableForm = z.infer<typeof freightTableSchema>;
type ProfileForm = z.infer<typeof profileSchema>;
type ChangePasswordForm = z.infer<typeof changePasswordSchema>;
type NotificationPreferencesForm = z.infer<typeof notificationPreferencesSchema>;
```

#### 3. UI State Types
```typescript
// Table
interface TableState<T> { data: T[]; total: number; page: number; size: number; sorting: SortingState; filters: FilterState; }

// Modals
interface ModalState { isOpen: boolean; data: T | null; mode: 'create' | 'edit' | 'view'; }

// Filters
interface DiscrepancyFilters { status?: DiscrepancyStatus[]; severity?: DiscrepancySeverity[]; rule_code?: string[]; date_from?: string; date_to?: string; search?: string; }
interface DocumentFilters { status?: DocumentStatus[]; document_type?: DocumentType[]; date_from?: string; date_to?: string; search?: string; }
```

#### 4. Enums (Mirror Backend)
```typescript
type UserRole = 'ADMIN' | 'MANAGER' | 'AUDITOR' | 'CLIENT' | 'CARRIER';
type UserStatus = 'ACTIVE' | 'INACTIVE' | 'PENDING';
type DocumentStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
type DocumentType = 'CTE' | 'NFE' | 'OTHER';
type DiscrepancyStatus = 'OPEN' | 'UNDER_REVIEW' | 'RESOLVED' | 'DISMISSED' | 'CONTESTED';
type DiscrepancySeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
type ContestStatus = 'DRAFT' | 'SENT' | 'ACKNOWLEDGED' | 'NEGOTIATING' | 'ACCEPTED' | 'PARTIAL' | 'REJECTED' | 'PAID';
type ContestItemStatus = 'PENDING' | 'ACKNOWLEDGED' | 'NEGOTIATING' | 'ACCEPTED' | 'PARTIAL' | 'REJECTED';
type NotificationType = 'DISCREPANCY_ALERT' | 'CONTEST_CREATED' | 'WEEKLY_REPORT' | 'CONTRACT_EXPIRING' | 'PAYMENT_RECEIVED' | 'WELCOME' | 'PASSWORD_RESET';
type NotificationChannel = 'EMAIL' | 'IN_APP' | 'PUSH';
type FreightTableStatus = 'DRAFT' | 'ACTIVE' | 'ARCHIVED';
type Modal = 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';
```

### Implementation Plan

1. **Create type files by domain:**
   - `frontend/src/types/auth.ts`
   - `frontend/src/types/documents.ts`
   - `frontend/src/types/discrepancies.ts`
   - `frontend/src/types/contests.ts`
   - `frontend/src/types/reports.ts`
   - `frontend/src/types/clients.ts`
   - `frontend/src/types/carriers.ts`
   - `frontend/src/types/contracts.ts`
   - `frontend/src/types/notifications.ts`
   - `frontend/src/types/ui.ts` (TableState, ModalState, Filters)
   - `frontend/src/types/enums.ts`

2. **Update barrel export:**
   - `frontend/src/types/index.ts` - export all from domain files

3. **Update imports across codebase:**
   - Replace inline types with imports from `@/types`
   - Remove duplicate type definitions

### Files to Modify
- `frontend/src/types/index.ts` - Main barrel (update)
- `frontend/src/types/*.ts` - New domain type files (create)
- All components/hooks/pages - Update imports (refactor)

## Dependencies
- Card #01: Testing infrastructure (DONE)
- All page cards (#10, #11, #15, #22-25) - Types needed for new pages

## Testing Requirements
- TypeScript compile check: `pnpm build` (tsc runs during build)
- No `any` types introduced
- All existing tests still pass
- No runtime errors from type changes

## Definition of Done
- [ ] All domain type files created
- [ ] Barrel export `frontend/src/types/index.ts` complete
- [ ] All inline types moved to centralized definitions
- [ ] All imports updated to use `@/types`
- [ ] TypeScript strict mode passes with zero errors
- [ ] All quality gates pass: `pnpm lint && pnpm build && pnpm test`
- [ ] Card moved to `review/`

## Notes
- This enables better type safety and IDE autocomplete
- Backend OpenAPI spec can be used to generate types (future: `openapi-typescript`)
- Keep enums in sync with backend Prisma schema
- Form types should be inferred from Zod schemas (single source of truth)