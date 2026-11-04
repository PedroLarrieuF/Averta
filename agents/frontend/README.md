# AvertaSaaS Frontend Agents (Legacy Structure)

> **Note:** This is the legacy agent structure. The new consolidated structure is in `agents-new/`. Each agent now manages their own Kanban board locally.

## New Structure: `agents-new/frontend-agent/`

```
agents-new/frontend-agent/
├── agent.md           # Consolidated agent config + Kanban
└── cards/             # Local Kanban board
    ├── backlog/
    ├── ready/
    ├── in-progress/
    ├── review/
    └── done/
```

## Legacy Folder Structure (Deprecated)

```
agents/frontend/
├── ui/                    # Design System & Components
│   └── ui-agent.md        # Components, layouts, styling, Radix UI, accessibility
├── pages/                 # Feature Page Implementations
│   └── pages-agent.md     # Documents, Discrepancies, Contests, Reports, Settings, etc.
├── state/                 # State Management & Data Fetching
│   └── state-agent.md     # TanStack Query, API client, Auth, Forms (RHF + Zod)
└── testing/               # Testing Infrastructure
    └── testing-agent.md   # Vitest, RTL, MSW, jest-axe, factories, coverage
```

## Agent Responsibilities (Legacy)

| Agent | Specialization | Sprint 1 Cards | Sprint 2 Cards |
|-------|---------------|----------------|----------------|
| **ui-agent** | Design system, components, layouts, charts | #03, #07 | - |
| **pages-agent** | Page implementations, feature composition | **#08, #09, #10** | **#11, #15** |
| **state-agent** | Hooks, API, auth, forms, types | All (provides hooks) | All (provides hooks) |
| **testing-agent** | Tests, MSW, factories, coverage | All (writes tests) | All (writes tests) |

## Coordination Protocol (Legacy)

### Workflow for Each Card

```
1. Tech Lead assigns card to pages-agent (moves to agents-new/frontend-agent/cards/ready/)
        │
        ▼
2. pages-agent requests hooks from state-agent
        │
        ▼
3. state-agent creates hooks + types + Zod schemas
        │
        ▼
4. pages-agent requests UI components from ui-agent
        │
        ▼
5. ui-agent creates/updates components
        │
        ▼
6. pages-agent composes page with hooks + components
        │
        ▼
7. testing-agent writes tests for all layers
        │
        ▼
8. Quality gates: pnpm lint && pnpm build && pnpm test
        │
        ▼
9. Move card: in-progress → review (in agents-new/frontend-agent/cards/)
```

### Delegation Examples (Updated for New Structure)

```python
# Implement Documents page (Sprint 1)
Agent(subagent_type="frontend-agent", prompt="Replace Documents ComingSoon with full implementation: upload, list, detail")

# Create hooks for Documents (state-agent handles this)
Agent(subagent_type="frontend-state-agent", prompt="Create useDocuments hooks: list, detail, upload, reprocess")

# Create UI components (ui-agent handles this)
Agent(subagent_type="frontend-ui-agent", prompt="Create UploadZone component with react-dropzone for Documents page")

# Write tests (testing-agent handles this)
Agent(subagent_type="frontend-testing-agent", prompt="Write full test suite for Documents page: components, hooks, integration")
```

## Sprint 1 Priority (Current)

| Card | Primary Agent | Support Agents |
|------|--------------|----------------|
| **#08** Documents Page | pages-agent | state-agent (hooks), ui-agent (UploadZone, Table, Modal), testing-agent (tests) |
| **#09** Discrepancies Page | pages-agent | state-agent (hooks), ui-agent (FilterSidebar, BulkActions), testing-agent |
| **#10** Contests Page | pages-agent | state-agent (hooks), ui-agent (Wizard, Timeline), testing-agent |
| #03 Dashboard Charts | ui-agent | state-agent (data hooks), testing-agent |

## Sprint 2 Priority

| Card | Primary Agent | Support Agents |
|------|--------------|----------------|
| **#11** Reports Page | pages-agent | state-agent, ui-agent (charts, export), testing-agent |
| **#15** Settings Pages | pages-agent | state-agent, ui-agent (Tabs, Forms, FreightTableEditor), testing-agent |

## Sprint 3+ (Backlog)

| Page | Primary Agent |
|------|--------------|
| Clients | pages-agent |
| Carriers | pages-agent |
| Contracts | pages-agent (needs FreightTableEditor from ui-agent) |
| Profile | pages-agent |

## Quality Gates (All Agents)

```bash
cd frontend
pnpm lint          # ESLint - zero errors
pnpm build         # tsc + vite build - zero errors
pnpm test          # Vitest - all pass
pnpm test:coverage # ≥70% lines, ≥70% functions, ≥60% branches
```

## Shared Conventions

### File Naming
- Components: `PascalCase.tsx` (e.g., `DocumentsTable.tsx`)
- Hooks: `useCamelCase.ts` (e.g., `useDocuments.ts`)
- Types: `types/index.ts` (barrel) + feature types
- Tests: `*.test.tsx` or `*.test.ts` (co-located or in `__tests__`)

### Import Aliases
```typescript
// tsconfig.json paths
"@/*": ["src/*"]
"@/components": ["src/components"]
"@/hooks": ["src/hooks"]
"@/pages": ["src/pages"]
"@/services": ["src/services"]
"@/store": ["src/store"]
"@/utils": ["src/utils"]
"@/test": ["src/test"]
"@/types": ["src/types"]
```

### Design System Usage
```typescript
// Always use design system classes from index.css
import { cn } from '@/utils/helpers'

<div className={cn('card', 'p-4')}>
  <Button variant="primary" className={cn('w-full', isLoading && 'opacity-50')}>
    Salvar
  </Button>
</div>
```

### State Patterns
```typescript
// Server state → TanStack Query hooks (state-agent)
// Client state → React useState/useReducer in component
// Form state → React Hook Form + Zod (state-agent)
// Auth state → useAuth() hook (already implemented)
```

## Usage

Each agent file contains:
- Specialized context and knowledge
- Relevant cards and tasks
- Implementation patterns
- Quality gates
- Coordination protocols

Load the appropriate agent based on the task at hand.

## Quick Reference

```bash
# Start working on Card #08 (Documents)
# 1. Check card details
cat cards/ready/08-documents-page-upload-list-detail.md

# 2. Delegate to pages-agent (orchestrates others)
Agent(subagent_type="frontend-pages-agent", prompt="Implement Card #08: Documents page with upload, list, detail")

# 3. Run dev server to verify
cd frontend && pnpm dev
```