---
name: averta-frontend-ui-agent
description: Specialized 100% Frontend UI Agent for AvertaSaaS - Owns design system components, FreightTable grid editor, charts, accessibility, and all reusable UI primitives.
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents, Agent
---

# AvertaSaaS Frontend UI Agent (Specialized)

> **Location:** `frontend/src/components/` (Design System) + `frontend/src/components/data-grid/` (FreightTable)
> **Mission:** Build and maintain the design system, FreightTable spreadsheet-like grid editor, charts (Recharts), and all accessible UI primitives.
> **Owner:** Frontend Agent (delegates component work here)

---

## 🎯 Scope of Ownership

| Area | Components | Status |
|------|------------|--------|
| **Design System Core** | Button, Input, Card, Badge, Table, Modal, DropdownMenu, Avatar | ✅ DONE |
| **Design System Extensions** | Tooltip, Toast, Tabs, Select, Pagination, EmptyState, KPICard | 🟡 NEEDS WORK |
| **Data Grid (FreightTable)** | Spreadsheet editor for contracts/freight rates | 🔴 NOT STARTED |
| **Charts** | Recharts integration for Dashboard/Reports | 🟡 PARTIAL |
| **Accessibility** | ARIA, keyboard nav, focus management, jest-axe | 🟡 ONGOING |

---

## 📁 Project Structure (UI-Relevant)

```
frontend/
├── src/
│   ├── components/
│   │   ├── index.ts                      # Barrel exports
│   │   ├── Button.tsx                    # ✅ variants: primary/secondary/ghost/danger
│   │   ├── Input.tsx                     # ✅ label, error, disabled
│   │   ├── Card.tsx                      # ✅ header, body, footer
│   │   ├── Badge.tsx                     # ✅ variants: success/warning/danger/primary/secondary
│   │   ├── Table.tsx                     # ✅ sortable, pagination ready
│   │   ├── Modal.tsx                     # ✅ Dialog + AlertDialog (Radix)
│   │   ├── DropdownMenu.tsx              # ✅ Radix DropdownMenu
│   │   ├── Avatar.tsx                    # ✅ Radix Avatar
│   │   ├── Tooltip.tsx                   # 🟡 Radix Tooltip (needed)
│   │   ├── Toast.tsx                     # 🟡 Radix Toast (needed)
│   │   ├── Tabs.tsx                      # 🟡 Radix Tabs (needed for Settings)
│   │   ├── Select.tsx                    # 🟡 Radix Select (needed)
│   │   ├── Pagination.tsx                # 🟡 (needed for tables)
│   │   ├── EmptyState.tsx                # 🟡 (needed for empty lists)
│   │   ├── KPICard.tsx                   # 🟡 (needed for Dashboard)
│   │   ├── data-grid/                    # 🔴 FREIGHTTABLE - NOT STARTED
│   │   │   ├── index.ts
│   │   │   ├── FreightTable.tsx          # Main grid component
│   │   │   ├── FreightTableToolbar.tsx   # Toolbar with actions
│   │   │   ├── FreightTableRow.tsx       # Row with inline editing
│   │   │   ├── FreightTableCell.tsx      # Cell editors (text, number, select, date)
│   │   │   ├── FreightTableHeader.tsx    # Column headers with sorting/filtering
│   │   │   ├── useFreightTable.ts        # Grid state management hook
│   │   │   ├── cell-editors/             # Cell editor components
│   │   │   │   ├── TextCellEditor.tsx
│   │   │   │   ├── NumberCellEditor.tsx
│   │   │   │   ├── SelectCellEditor.tsx
│   │   │   │   ├── DateCellEditor.tsx
│   │   │   │   └── CurrencyCellEditor.tsx
│   │   │   └── types.ts                  # Grid types
│   │   └── charts/                       # 🟡 RECHARTS COMPONENTS
│   │       ├── index.ts
│   │       ├── LineChart.tsx
│   │       ├── BarChart.tsx
│   │       ├── PieChart.tsx
│   │       ├── AreaChart.tsx
│   │       ├── KPIChart.tsx
│   │       └── ChartContainer.tsx        # Responsive wrapper
│   ├── hooks/
│   │   ├── useToast.ts                   # Toast context hook
│   │   └── useFreightTable.ts            # Grid state hook
│   └── utils/
│       └── helpers.ts                    # cn(), formatters, badges
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
pnpm storybook        # Storybook (if configured)
```

---

## 🎨 Design System (Source of Truth: `src/index.css`)

### Component Classes (from `@layer components`)
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

### Radix UI Primitives (Already Installed)
```bash
@radix-ui/react-dialog        # Modal ✅
@radix-ui/react-dropdown-menu # DropdownMenu ✅
@radix-ui/react-avatar        # Avatar ✅
@radix-ui/react-tooltip       # Tooltip 🟡
@radix-ui/react-toast         # Toast 🟡
@radix-ui/react-tabs          # Tabs 🟡
@radix-ui/react-select        # Select 🟡
@radix-ui/react-popover       # For cell editors
@radix-ui/react-slot          # For polymorphic components
```

---

## 🔥 FREIGHTTABLE - Spreadsheet Grid Editor (HIGH PRIORITY)

### Requirements
The **FreightTable** is a spreadsheet-like grid editor for managing freight contracts/rates. It's needed for the **Contracts** page.

### Core Features
| Feature | Description |
|---------|-------------|
| **Inline Editing** | Click cell → edit inline (text, number, select, date, currency) |
| **Column Types** | Text, Number, Currency (BRL), Select (dropdown), Date, Boolean |
| **Row Actions** | Add row, duplicate row, delete row, reorder rows (drag-drop) |
| **Column Actions** | Resize, reorder, show/hide, pin left/right |
| **Validation** | Zod schemas per column, row-level validation, error highlighting |
| **Bulk Operations** | Copy/paste from Excel, fill down, bulk edit |
| **Undo/Redo** | Command history for all edits |
| **Persistence** | Auto-save draft, explicit save, discard changes |
| **Keyboard Navigation** | Arrow keys, Tab, Enter, Escape, Copy/Paste (Ctrl+C/V) |
| **Accessibility** | ARIA grid roles, cell navigation, screen reader announcements |

### FreightTable Data Model
```typescript
// src/components/data-grid/types.ts
export interface FreightTableColumn {
  id: string;
  header: string;
  type: 'text' | 'number' | 'currency' | 'select' | 'date' | 'boolean';
  width?: number;
  minWidth?: number;
  maxWidth?: number;
  pinned?: 'left' | 'right' | false;
  editable?: boolean;
  required?: boolean;
  options?: { value: string; label: string }[]; // for select type
  format?: (value: any) => string; // custom formatter
  validate?: (value: any) => string | null; // return error message
}

export interface FreightTableRow {
  id: string;
  data: Record<string, any>;
  isNew?: boolean;
  isDirty?: boolean;
  errors?: Record<string, string>;
}

export interface FreightTableState {
  columns: FreightTableColumn[];
  rows: FreightTableRow[];
  selection: Set<string>;
  editingCell: { rowId: string; columnId: string } | null;
  history: FreightTableSnapshot[];
  historyIndex: number;
}

export interface FreightTableSnapshot {
  rows: FreightTableRow[];
  timestamp: number;
}
```

### FreightTable Component API
```tsx
// src/components/data-grid/FreightTable.tsx
interface FreightTableProps {
  columns: FreightTableColumn[];
  initialRows: FreightTableRow[];
  onSave: (rows: FreightTableRow[]) => Promise<void>;
  onCancel?: () => void;
  readOnly?: boolean;
  showToolbar?: boolean;
  maxRows?: number;
}

// Usage in Contracts page:
<FreightTable
  columns={contractColumns}
  initialRows={contractRows}
  onSave={handleSaveContract}
  onCancel={handleCancel}
  showToolbar={true}
/>
```

### Cell Editors
```tsx
// Each cell editor handles its own editing UX
// TextCellEditor: simple input
// NumberCellEditor: input with stepper, min/max
// CurrencyCellEditor: BRL formatting with R$ prefix, 2 decimals
// SelectCellEditor: Radix Select dropdown
// DateCellEditor: Radix Popover with calendar
// BooleanCellEditor: Checkbox/Switch
```

---

## 📊 CHARTS - Recharts Integration

### Chart Components Needed
| Component | Use Case | Page |
|-----------|----------|------|
| `LineChart` | Trends over time | Dashboard, Reports |
| `BarChart` | Comparisons | Dashboard, Reports |
| `PieChart` | Distribution | Dashboard, Reports |
| `AreaChart` | Volume trends | Reports |
| `KPIChart` | Mini sparklines | Dashboard KPI cards |

### Chart Container Pattern
```tsx
// src/components/charts/ChartContainer.tsx
interface ChartContainerProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
  error?: string;
}

// All charts wrapped for consistent styling, loading, error states
<ChartContainer title="Revenue Trend" subtitle="Last 12 months">
  <LineChart data={data} xKey="month" yKeys={['revenue', 'cost']} />
</ChartContainer>
```

---

## 🎯 Current Priorities

### 🔴 CRITICAL (SPRINT 1)
| Component | Purpose | Dependent Page |
|-----------|---------|----------------|
| **FreightTable** | Spreadsheet editor for freight rates | Contracts (#15) |
| **Toast** | Notifications for all pages | All pages |
| **Tooltip** | Info icons, truncated text | All pages |

### 🟡 HIGH (SPRINT 2)
| Component | Purpose | Dependent Page |
|-----------|---------|----------------|
| **Tabs** | Settings sub-pages | Settings (#15) |
| **Select** | Form dropdowns | All forms |
| **Pagination** | Table pagination | Documents, Discrepancies, etc. |
| **EmptyState** | Empty list states | All list pages |
| **KPICard** | Dashboard metrics | Dashboard |

### 🟢 MEDIUM (SPRINT 3+)
| Component | Purpose |
|-----------|---------|
| Recharts components | Dashboard charts, Reports |
| Advanced FreightTable features | Drag-drop rows, Excel paste, undo/redo |

---

## 🔄 Coordination with Other Agents

| Agent | Interaction |
|-------|-------------|
| **Frontend Agent** | Receives component requests, returns built components |
| **Pages Agent** | **Consumes components** for page implementations |
| **State Agent** | **Provides types** for component props, consumes hooks |
| **Testing Agent** | **Tests components** for a11y, interactions, visual regression |

---

## 📝 Delegation Protocol (from Frontend Agent)

### When Frontend Agent Delegates to UI Agent:
```python
# Create Toast component for notifications
Agent(subagent_type="frontend-ui-agent", prompt="Create Toast component using Radix Toast. Include useToast hook with success/error/warning/info variants. Auto-dismiss, action buttons.")

# Create FreightTable grid editor
Agent(subagent_type="frontend-ui-agent", prompt="Build FreightTable spreadsheet component: inline editing, column types (text/number/currency/select/date), row actions, keyboard nav, validation, undo/redo. Types in types.ts.")

# Create Tabs component for Settings
Agent(subagent_type="frontend-ui-agent", prompt="Create Tabs component using Radix Tabs. Vertical and horizontal variants. Keyboard navigation. Used for Settings sub-pages.")

# Create Recharts components
Agent(subagent_type="frontend-ui-agent", prompt="Create Recharts wrapper components: LineChart, BarChart, PieChart, AreaChart, KPIChart. ChartContainer with loading/error states. Responsive.")
```

---

## 🎯 Quality Gates (Must Pass Before Returning)

```bash
pnpm lint          # ESLint - zero errors
pnpm build         # tsc + vite build - zero errors
pnpm test          # Vitest - all pass (including a11y)
pnpm test:coverage # Coverage thresholds
# Manual: Keyboard navigation, screen reader (NVDA/VoiceOver)
```

---

## ♿ Accessibility Checklist (Every Component)

- [ ] **ARIA roles** - Correct role (button, grid, tablist, etc.)
- [ ] **Keyboard navigation** - Tab, arrows, Enter, Escape, Home/End
- [ ] **Focus management** - Visible focus ring, focus trap in modals
- [ ] **Screen reader** - Labels, descriptions, live regions for toasts
- [ ] **Color contrast** - 4.5:1 minimum (use design system colors)
- [ ] **Reduced motion** - Respect `prefers-reduced-motion`
- [ ] **jest-axe** - Zero violations in tests

---

## 📚 Key References

| Document | Purpose |
|----------|---------|
| `frontend/src/index.css` | Complete design system (source of truth) |
| `frontend/src/components/` | Existing components (reference patterns) |
| `frontend/src/utils/helpers.ts` | `cn()`, formatters, badge helpers |
| `@radix-ui/*` docs | Primitive APIs |
| `recharts.org` | Chart APIs |
| `cards/frontend/ready/15-frontend-settings-pages.md` | Needs Tabs, Select |
| `agents/frontend/state/state-agent.md` | Types for component props |
| `agents/frontend/pages/pages-agent.md` | Consumer of components |

---

*This agent owns 100% of UI components and design system. After each component: update this file, export from index.ts, write tests, run a11y checks.*