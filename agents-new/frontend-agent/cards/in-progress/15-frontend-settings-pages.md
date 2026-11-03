---
id: 15
title: "Build Settings Pages (Company, Users, Carriers, Contracts, Notifications)"
priority: high
type: feature
agent: frontend
sprint: 3
estimate: XL
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 15: Build Settings Pages

## Contexto
Área administrativa: configurações da empresa, usuários, transportadoras, contratos, notificações.

## Definition of Ready
- [x] APIs: Companies, Users, Carriers, Contracts, Notifications (CRUD completo)
- [x] Design system + forms prontos (Cards 07, 02)
- [x] RBAC: apenas ADMIN/MANAGER acessam

## Tasks
- [ ] `src/pages/SettingsLayout.tsx` - sidebar navegação + outlet
- [ ] `src/pages/settings/CompanySettingsPage.tsx` - dados empresa, logo, CNPJ
- [ ] `src/pages/settings/UsersPage.tsx` - listagem, convidar, editar role/status
- [ ] `src/pages/settings/CarriersPage.tsx` - CRUD transportadoras
- [ ] `src/pages/settings/ContractsPage.tsx` - CRUD contratos + tabelas de frete
- [ ] `src/pages/settings/NotificationsPage.tsx` - preferências, templates email
- [ ] `src/pages/settings/FreightTablePage.tsx` - versionamento, regras JSON
- [ ] Hooks para cada módulo (CRUD + validações)
- [ ] Componentes reutilizáveis:
  - `src/components/settings/UserInviteModal.tsx`
  - `src/components/settings/ContractForm.tsx` (complexo - tabelas de frete)
  - `src/components/settings/FreightTableEditor.tsx` - JSON editor para rules
- [ ] Permissões: hide/show baseado em role (hasRole)
- [ ] Testes: CRUD flows, permissions

## Acceptance Criteria
- [ ] ADMIN vê todas abas, MANAGER vê subset, CLIENT não vê
- [ ] CRUD funcional em todas entidades
- [ ] Contract form suporta versionamento de tabelas
- [ ] Freight table editor valida JSON schema
- [ ] Notificações: preferências por canal/tipo
- [ ] Testes integração

## Referências
- `backend/README.md` - seção "Gestão de Entidades"
- `frontend/utils/helpers.ts` - ROLES, hasRole