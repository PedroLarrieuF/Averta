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
Sistema de design base para toda a aplicação. Componentes reutilizáveis, acessíveis, com variantes consistentes.

## Definition of Ready
- [x] Tailwind + CSS variables configurados em `index.css`
- [x] Radix UI primitives instalados
- [x] `cn()` utility (clsx + tailwind-merge) disponível

## Tasks
### Componentes Base (já implementados - verificar e validar)
- [ ] `src/components/Button.tsx` - variants: primary, secondary, ghost, danger; sizes: sm, md, lg; loading state; icon support
- [ ] `src/components/Input.tsx` - label, error, disabled, helper text, icon
- [ ] `src/components/Card.tsx` - Card, Card.Header, Card.Body, Card.Footer
- [ ] `src/components/Badge.tsx` - variants: success, warning, danger, primary, secondary, outline
- [ ] `src/components/Table.tsx` - sortable columns, pagination ready, empty state, loading skeleton
- [ ] `src/components/Modal.tsx` - Dialog + AlertDialog (Radix), sizes, portal
- [ ] `src/components/DropdownMenu.tsx` - Radix DropdownMenu, submenus, separators
- [ ] `src/components/Avatar.tsx` - Radix Avatar, fallback initials, sizes

### Componentes Adicionais (precisam ser criados)
- [ ] `src/components/Tooltip.tsx` - Radix Tooltip, delay, side/align
- [ ] `src/components/Toast.tsx` - Radix Toast, toast provider, variants, action buttons
- [ ] `src/components/Tabs.tsx` - Radix Tabs, controlled/uncontrolled
- [ ] `src/components/Select.tsx` - Radix Select, searchable, multi-select
- [ ] `src/components/Pagination.tsx` - page numbers, prev/next, page size selector
- [ ] `src/components/EmptyState.tsx` - icon, title, description, action button
- [ ] `src/components/KPICard.tsx` - value, label, trend (up/down), icon, loading skeleton

### CSS Classes (em `index.css` @layer components)
- [ ] `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-lg`
- [ ] `.input`, `.input-error`, `.label`
- [ ] `.card`, `.card-header`, `.card-body`, `.card-footer`
- [ ] `.badge`, `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-primary`, `.badge-secondary`
- [ ] `.table-container`, `.table`, `.table th`, `.table td`
- [ ] `.modal-overlay`, `.modal-content`, `.modal-header`, `.modal-body`, `.modal-footer`
- [ ] `.empty-state`, `.empty-state-icon`, `.empty-state-title`, `.empty-state-description`
- [ ] `.kpi-card`, `.kpi-value`, `.kpi-label`, `.kpi-trend`
- [ ] `.pagination`, `.pagination-item`, `.pagination-item-active`
- [ ] `.tabs-trigger`, `.tabs-trigger-active`, `.tabs-content`

### Barrel Exports
- [ ] `src/components/index.ts` - export all components

### Testes
- [ ] Testes de renderização para cada componente
- [ ] Testes de variantes (Button variants, Badge variants)
- [ ] Testes de acessibilidade (jest-axe) - foco, ARIA, keyboard navigation
- [ ] Testes de interação (Modal open/close, Dropdown select, Tabs)

## Acceptance Criteria
- [ ] Todos os 15 componentes renderizam sem erros
- [ ] Variantes funcionam conforme design system
- [ ] Acessibilidade: 100% jest-axe pass
- [ ] TypeScript strict - sem `any`
- [ ] Storybook/Visual regression ready (opcional)
- [ ] Documentação de uso em cada componente (JSDoc)

## Referências
- `frontend/src/index.css` - Design system CSS classes
- `frontend/src/utils/helpers.ts` - `cn()` utility
- Radix UI docs: https://www.radix-ui.com/
- Tailwind CSS: https://tailwindcss.com/