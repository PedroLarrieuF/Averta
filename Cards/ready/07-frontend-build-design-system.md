---
id: 07
title: "Build Design System Components (Button, Input, Card, Badge, Table, Modal)"
priority: critical
type: feature
agent: frontend
sprint: 1
estimate: L
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 07: Build Design System Components

## Contexto
`index.css` define classes CSS mas **componentes React não existem**. Precisa criar componentes base reutilizáveis.

## Definition of Ready
- [x] Design system CSS pronto (index.css com @layer components)
- [x] Radix UI instalado (Dialog, DropdownMenu, Tabs, Select, etc.)
- [x] clsx + tailwind-merge configurados (cn utility)

## Tasks
- [ ] `src/components/ui/Button.tsx` - variants: primary, secondary, ghost, danger, sizes
- [ ] `src/components/ui/Input.tsx` - label, error, disabled, variants
- [ ] `src/components/ui/Card.tsx` - header, body, footer
- [ ] `src/components/ui/Badge.tsx` - variants: success, warning, danger, primary, secondary
- [ ] `src/components/ui/Table.tsx` - sortable, pagination, row actions
- [ ] `src/components/ui/Modal.tsx` - Dialog + AlertDialog (Radix)
- [ ] `src/components/ui/DropdownMenu.tsx` - Radix DropdownMenu
- [ ] `src/components/ui/Tabs.tsx` - Radix Tabs
- [ ] `src/components/ui/Select.tsx` - Radix Select
- [ ] `src/components/ui/Toast.tsx` - react-hot-toast wrapper
- [ ] `src/components/ui/Avatar.tsx` - Radix Avatar
- [ ] `src/components/ui/SidebarLink.tsx` - active/inactive
- [ ] `src/components/ui/KPICard.tsx` - para dashboard
- [ ] `src/components/ui/EmptyState.tsx`
- [ ] `src/components/ui/PageHeader.tsx`
- [ ] Storybook setup (opcional) ou página de docs interna
- [ ] Testes unitários para cada componente (Vitest + RTL)

## Component API Pattern
```tsx
// Exemplo Button
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: React.ReactNode
}
```

## Acceptance Criteria
- [ ] Todos os componentes usam classes do index.css
- [ ] TypeScript strict - props tipadas
- [ ] Acessibilidade (ARIA, focus management via Radix)
- [ ] Testes: render, variants, interactions, a11y
- [ ] Documentação de uso (props, exemplos)

## Referências
- `packages/frontend/src/index.css` - @layer components
- `frontend-agent.md` - Design System section
- Radix UI docs: https://www.radix-ui.com/