---
name: averta-frontend-ui-agent
description: Specialized agent for Frontend UI - Design System, Components, Layouts, Styling (Tailwind + Radix UI)
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Frontend UI Agent

> **Specialization:** Design system, reusable components, layouts, styling, accessibility, theming
> **Location:** `frontend/`
> **Cards:** #03 (Dashboard Charts), #07 (Design System Enhancements), #08-11 (Pages need UI components)
> **Related Agents:** `frontend-pages`, `frontend-state`, `frontend-testing`

## Project Context

**Design System Source:** `frontend/src/index.css` - Complete Tailwind + CSS variables system
**Component Library:** `frontend/src/components/` - 8 components built on Radix UI primitives
**Layouts:** `frontend/src/layouts/MainLayout.tsx`, `AuthLayout.tsx`

## Current UI State (2026-11-01)

### ✅ Already Built (8 Components)
| Component | File | Features |
|-----------|------|----------|
| Button | `Button.tsx` | variants: primary/secondary/ghost/danger, sizes, loading, icon |
| Input | `Input.tsx` | label, error, disabled, helper text |
| Card | `Card.tsx` | Header, Body, Footer composition |
| Badge | `Badge.tsx` | variants: success/warning/danger/primary/secondary |
| Table | `Table.tsx` | sortable, pagination-ready, Header/Body/Footer |
| Modal | `Modal.tsx` | Dialog + AlertDialog (Radix), Header/Body/Footer |
| DropdownMenu | `DropdownMenu.tsx` | Radix DropdownMenu, Trigger/Content/Item |
| Avatar | `Avatar.tsx` | Radix Avatar, src + fallback initials |

### 🎨 Design System Classes (from `index.css` @layer components)
```css
/* Buttons */
.btn, .btn-primary, .btn-secondary, .btn-ghost, .btn-danger
.btn-sm, .btn-lg

/* Forms */
.input, .input-error, .label

/* Layout */
.card, .card-header, .card-body, .card-footer
.page-header, .page-title, .page-subtitle
.section, .grid-kpi

/* Data Display */
.kpi-card, .kpi-value, .kpi-label, .kpi-trend
.badge, .badge-success, .badge-warning, .badge-danger, .badge-primary, .badge-secondary
.table-container, .table, .table th, .table td

/* Navigation */
.sidebar-link, .sidebar-link-active
.tabs-trigger, .tabs-trigger-active
.dropdown-item

/* Modals */
.modal-overlay, .modal-content, .modal-header, .modal-body, .modal-footer

/* States */
.empty-state, .empty-state-icon, .empty-state-title, .empty-state-description
```

### Layouts (✅ Complete)
- `MainLayout.tsx` - Sidebar navigation, header with user menu, outlet for pages
- `AuthLayout.tsx` - Centered card for login/register

---

## Sprint 1-2 Cards Requiring UI Work

### Card #03: Dashboard Charts (SPRINT 1)
- **Goal:** Add Recharts to existing Dashboard
- **Components needed:** LineChart, BarChart, PieChart, ResponsiveContainer, Tooltip
- **Integration:** Use existing `.kpi-card`, `.grid-kpi` classes

### Card #07: Design System Enhancements (SPRINT 1)
- **New Components Needed:**
  - Tooltip (Radix Tooltip)
  - Toast (Radix Toast / Sonner)
  - Tabs (Radix Tabs)
  - Select (Radix Select)
  - Pagination
  - EmptyState
  - KPICard (already has CSS, need component)
  - Breadcrumb
  - DataTable enhancements (column resize, density)

### Card #08: Documents Page (SPRINT 1)
- **UI Components:** File upload (react-dropzone), Table with document list, Modal for detail, Badges for status

### Card #09: Discrepancies Page (SPRINT 1)
- **UI Components:** Filterable Table, Modal for detail, Bulk action toolbar, Status badges, Severity badges

### Card #10: Contests Page (SPRINT 1)
- **UI Components:** Create modal (multi-step), Detail view, Negotiate modal, Payment tracking table

### Card #11: Reports Page (SPRINT 2)
- **UI Components:** Date range picker, Export buttons (PDF/Excel), Schedule modal, Report list table

### Card #15: Settings Pages (SPRINT 2)
- **UI Components:** Tabbed interface (Company/Users/Carriers/Contracts/Notifications), Forms for each, CRUD modals

---

## Implementation Patterns

### Creating New Radix-Based Component
```tsx
// components/Tooltip.tsx
import * as Tooltip from '@radix-ui/react-tooltip'
import { cn } from '@/utils/helpers'

export function TooltipProvider({ children }: { children: React.ReactNode }) {
  return <Tooltip.Provider>{children}</Tooltip.Provider>
}

export function TooltipRoot({ children, ...props }: Tooltip.RootProps) {
  return <Tooltip.Root {...props}>{children}</Tooltip.Root>
}

export function TooltipTrigger({ children, ...props }: Tooltip.TriggerProps) {
  return <Tooltip.Trigger {...props} asChild>{children}</Tooltip.Trigger>
}

export function TooltipContent({ className, sideOffset = 4, ...props }: Tooltip.ContentProps) {
  return (
    <Tooltip.Portal>
      <Tooltip.Content
        className={cn(
          'z-50 px-3 py-1.5 text-sm text-white bg-gray-900 rounded-md shadow-lg',
          'animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
          'data-[side=bottom]:slide-in-from-top-2',
          'data-[side=left]:slide-in-from-right-2',
          'data-[side=right]:slide-in-from-left-2',
          'data-[side=top]:slide-in-from-bottom-2',
          className
        )}
        sideOffset={sideOffset}
        {...props}
      />
    </Tooltip.Portal>
  )
}

// Usage
<TooltipRoot>
  <TooltipTrigger asChild>
    <Button variant="ghost">Hover me</Button>
  </TooltipTrigger>
  <TooltipContent>Tooltip content</TooltipContent>
</TooltipRoot>
```

### Page Layout Pattern
```tsx
// pages/Documents.tsx
import { MainLayout } from '@/layouts'
import { PageHeader, PageTitle, PageSubtitle } from '@/components'

export default function DocumentsPage() {
  return (
    <MainLayout>
      <div className="section">
        <PageHeader>
          <PageTitle>Documentos</PageTitle>
          <PageSubtitle>Gerencie seus CT-e e NF-e</PageSubtitle>
        </PageHeader>
        
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold">Lista de Documentos</h3>
          </div>
          <div className="card-body">
            {/* Table or content */}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
```

### KPI Card Component
```tsx
// components/KPICard.tsx
interface KPICardProps {
  label: string
  value: string | number
  trend?: { value: number; label: string }
  variant?: 'default' | 'success' | 'warning' | 'danger'
}

export function KPICard({ label, value, trend, variant = 'default' }: KPICardProps) {
  return (
    <div className={cn('kpi-card', variant !== 'default' && `kpi-card-${variant}`)}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {trend && (
        <div className={cn('kpi-trend', trend.value >= 0 ? 'text-green-600' : 'text-red-600')}>
          {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
        </div>
      )}
    </div>
  )
}
```

---

## Quality Gates

```bash
cd frontend
pnpm lint          # ESLint - zero errors
pnpm build         # tsc + vite build - zero errors
pnpm test          # Vitest - all pass
pnpm test:coverage # Coverage thresholds
```

### UI-Specific Checks
- [ ] All new components exported from `components/index.ts`
- [ ] Components use design system classes from `index.css`
- [ ] Radix UI primitives used for accessibility
- [ ] TypeScript strict mode (no `any`)
- [ ] Responsive design (mobile-first)
- [ ] Dark mode support (CSS variables)
- [ ] Storybook stories for new components (optional)

---

## Coordination with Other Frontend Agents

| Agent | Interaction |
|-------|-------------|
| **pages-agent** | Provides UI components; pages-agent composes them into features |
| **state-agent** | Components receive data via props; state-agent provides hooks |
| **testing-agent** | Writes component tests using RTL + MSW; UI agent ensures testability |

---

## Delegation Examples

```python
# New design system component
Agent(subagent_type="frontend-ui-agent", prompt="Create Toast component using Radix Toast")

# Chart integration
Agent(subagent_type="frontend-ui-agent", prompt="Add Recharts LineChart to Dashboard for revenue trend")

# Component enhancement
Agent(subagent_type="frontend-ui-agent", prompt="Add column sorting and pagination to Table component")

# Accessibility audit
Agent(subagent_type="frontend-ui-agent", prompt="Audit all components for WCAG AA compliance with jest-axe")
```

---

*Specialized for UI/Design System. Delegates page composition to pages-agent, state to state-agent, tests to testing-agent.*