# Frontend UI Agent - AvertaSaaS

## Overview
This agent is responsible for building and maintaining critical UI components for the AvertaSaaS frontend application.

## Created Components

### 1. Toast Component (Priority 1)
**Files:**
- `src/components/Toast.tsx` - Toast component using Radix Toast primitives
- Includes `Toast`, `ToastManager`, and `useToast` hook

**Features:**
- Radix UI Toast integration (@radix-ui/react-toast)
- Four variants: default, success, warning, danger
- Programmable API via `useToast()` hook
- ToastManager context provider for global toast management
- Auto-dismiss with configurable duration
- Swipe to dismiss support
- Action button support

**Usage:**
```tsx
import { ToastManager, useToast } from '@/components'

// In your app root
<ToastManager>
  <App />
</ToastManager>

// In any component
const { addToast, removeToast } = useToast()
addToast({ title: 'Sucesso', description: 'Operação realizada', variant: 'success' })
```

---

### 2. Tabs Component (Priority 2)
**File:**
- `src/components/Tabs.tsx` - Tabs component using Radix Tabs primitives

**Features:**
- Radix UI Tabs integration (@radix-ui/react-tabs)
- Controlled and uncontrolled modes
- Keyboard navigation (arrow keys, home, end)
- Animated transitions (fade + zoom)
- Focus management and accessibility (ARIA)
- Customizable styling via className props

**Exports:**
- `Tabs` (Root)
- `TabsList`
- `TabsTrigger`
- `TabsContent`
- `TabsProps` (types)

**Usage:**
```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components'

<Tabs value={activeTab} onValueChange={setActiveTab}>
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

---

### 3. Select Component (Priority 3)
**File:**
- `src/components/Select.tsx` - Select component using Radix Select primitives

**Features:**
- Radix UI Select integration (@radix-ui/react-select)
- Full keyboard navigation
- Search/filter support
- Grouping with SelectGroup/SelectLabel
- Scroll buttons for long lists
- Portal-based positioning
- Checkmark indicator for selected item
- Disabled states
- Customizable styling

**Exports:**
- `Select` (Root)
- `SelectGroup`
- `SelectValue`
- `SelectTrigger`
- `SelectContent`
- `SelectLabel`
- `SelectItem`
- `SelectSeparator`
- `SelectScrollUpButton`
- `SelectScrollDownButton`
- `SelectProps` (types)

**Usage:**
```tsx
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components'

<Select value={value} onValueChange={setValue}>
  <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Opção 1</SelectItem>
    <SelectItem value="option2">Opção 2</SelectItem>
  </SelectContent>
</Select>
```

---

### 4. FreightTable Grid Editor (Priority 4)
**Files:**
- `src/components/data-grid/FreightTable.tsx` - Spreadsheet-like grid editor
- `src/components/data-grid/FreightTable.test.tsx` - Unit tests
- `src/components/data-grid/index.ts` - Exports

**Features:**
- Spreadsheet-like editing experience
- Inline cell editing (double-click or Enter to edit)
- Keyboard navigation (Tab, Arrow keys, Enter, Escape)
- Copy/Paste row support (Ctrl+C, Ctrl+V)
- Duplicate row (Ctrl+D)
- Delete row (Delete key or button)
- Column types: text, number, currency, select
- Required field validation indicators
- Custom cell renderers
- Row numbers
- Action buttons (duplicate, delete)
- Add new row button
- Max rows limit
- Sticky header
- Responsive horizontal scroll

**Column Configuration:**
```tsx
interface FreightTableColumn {
  key: string
  header: string
  type: 'text' | 'number' | 'currency' | 'select'
  width?: string
  options?: { value: string; label: string }[] // for select type
  required?: boolean
  editable?: boolean
  render?: (value: unknown, row: FreightTableRow) => React.ReactNode
}
```

**Usage:**
```tsx
import { FreightTable } from '@/components/data-grid'
import type { FreightTableColumn, FreightTableRow } from '@/components/data-grid'

const columns: FreightTableColumn[] = [
  { key: 'originCity', header: 'Cidade Origem', type: 'text', required: true },
  { key: 'freightType', header: 'Tipo Frete', type: 'select', required: true, options: [
    { value: 'NORMAL', label: 'Normal' },
    { value: 'EXPRESS', label: 'Expresso' },
  ]},
  { key: 'value', header: 'Valor', type: 'currency', required: true },
]

const data: FreightTableRow[] = [
  { id: '1', originCity: 'São Paulo', freightType: 'NORMAL', value: 500 },
]

<FreightTable
  columns={columns}
  data={data}
  onChange={setData}
  onAddRow={handleAdd}
  onDeleteRow={handleDelete}
  onDuplicateRow={handleDuplicate}
/>
```

---

## Dependencies
All components use Radix UI primitives:
- `@radix-ui/react-toast` ^1.1.5
- `@radix-ui/react-tabs` ^1.0.4
- `@radix-ui/react-select` ^2.0.0

## Styling
Components use Tailwind CSS with:
- `clsx` for conditional classes
- `tailwind-merge` for merging class names
- Custom `cn()` utility from `@/utils/helpers`

## Testing
- Vitest + React Testing Library
- Run tests: `pnpm test`
- Run tests with UI: `pnpm test:ui`
- Coverage: `pnpm test:coverage`

## Building
- TypeScript compilation: `pnpm build`
- Linting: `pnpm lint`