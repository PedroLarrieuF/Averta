# Agent Invocation Commands

Reference for calling each specialized agent via the `Agent` tool.

---

## 🎯 Main Tech Lead Agents

### Tech Lead (Frontend + PO + Architecture)
```python
Agent(
    subagent_type="techlead",
    prompt="Sua instrução aqui"
)
```
**Responsabilidades:** Frontend code review, PO coordination, architectural decisions, ADRs, cross-team coordination

---

### Backend Tech Lead (Code Review Specialist)
```python
Agent(
    subagent_type="backend-techlead-agent",
    prompt="Review PR #XXX: [descrição da feature backend]"
)
```
**Responsabilidades:** Backend code reviews apenas (Python FastAPI), delega para agentes especializados quando necessário

---

## 🐍 Backend Specialized Agents (5 agentes)

### Core Agent (Módulos, API, DB, Celery)
```python
Agent(
    subagent_type="core-agent",
    prompt="Sua instrução para desenvolvimento backend geral"
)
```
**Use para:** Novos módulos, CRUD, API endpoints, database operations, Celery tasks, XML parser fixes

---

### Rules Engine Agent (Rules Engine v2)
```python
Agent(
    subagent_type="rules-engine-agent",
    prompt="Sua instrução para Rules Engine"
)
```
**Use para:** Novas regras de auditoria, DB-driven rules, JSON logic, versioning, tag filtering O(tag)

---

### Integrations Agent (Webhooks, ERP/TMS, Email, S3)
```python
Agent(
    subagent_type="integrations-agent",
    prompt="Sua instrução para integrações externas"
)
```
**Use para:** Webhooks, ERP/TMS, EDI, Email (SendGrid), Storage (MinIO/S3), HMAC signatures

---

### Core Infra Agent (Audit, Soft Delete, Rate Limit, Middleware)
```python
Agent(
    subagent_type="core-infra-agent",
    prompt="Sua instrução para infraestrutura core"
)
```
**Use para:** Audit log middleware, soft delete global, rate limiting Redis, security middleware

---

### ML Agent (Anomaly Detection, Isolation Forest)
```python
Agent(
    subagent_type="ml-agent",
    prompt="Sua instrução para ML/Anomaly Detection"
)
```
**Use para:** Isolation Forest training, model serving, feature engineering, drift monitoring, feedback loop

---

## ⚛️ Frontend Specialized Agents (4 agentes)

### UI Agent (Design System, Components, Layouts)
```python
Agent(
    subagent_type="frontend-ui-agent",
    prompt="Sua instrução para UI/Design System"
)
```
**Use para:** Novos componentes Radix, charts (Recharts), acessibilidade, dark mode, design tokens

---

### Pages Agent (Implementação de Páginas/Features)
```python
Agent(
    subagent_type="frontend-pages-agent",
    prompt="Sua instrução para implementação de páginas"
)
```
**Use para:** Documents, Discrepancies, Contests, Reports, Settings, Clients, Carriers, Contracts, Profile

---

### State Agent (TanStack Query, API, Auth, Forms)
```python
Agent(
    subagent_type="frontend-state-agent",
    prompt="Sua instrução para state management"
)
```
**Use para:** Hooks TanStack Query, API client, React Hook Form + Zod, TypeScript types, error handling

---

### Testing Agent (Vitest, RTL, MSW, jest-axe)
```python
Agent(
    subagent_type="frontend-testing-agent",
    prompt="Sua instrução para testes"
)
```
**Use para:** Component tests, hook tests, integration tests, MSW handlers, factories, coverage, a11y

---

## 📋 Business / PO Agent

### PO Scrum Agent (Requisitos, Regras Regulatórias)
```python
Agent(
    subagent_type="po-scrum-agent",
    prompt="Sua instrução para coordenação com PO"
)
```
**Use para:** Clarificar critérios de aceitação, validar regras regulatórias, sprint planning, demo/UAT

---

## 🔧 Common Delegation Patterns

### Frontend Feature Implementation (Full Stack)
```python
# 1. Tech Lead orquestra - cria hooks
Agent(subagent_type="frontend-state-agent", prompt="Create useDocuments hooks: list, detail, upload, reprocess")

# 2. Tech Lead orquestra - cria componentes UI
Agent(subagent_type="frontend-ui-agent", prompt="Create UploadZone component with react-dropzone for Documents page")

# 3. Tech Lead orquestra - implementa página
Agent(subagent_type="frontend-pages-agent", prompt="Replace Documents ComingSoon with full implementation: upload, list, detail")

# 4. Tech Lead orquestra - escreve testes
Agent(subagent_type="frontend-testing-agent", prompt="Write full test suite for Documents page: components, hooks, integration")
```

### Backend Feature Implementation
```python
# Backend Tech Lead recebe PR e revisa
Agent(subagent_type="backend-techlead-agent", prompt="Review PR #123: new clients module with CRUD")

# Para deep dive técnico, delega ao especialista
Agent(subagent_type="rules-engine-agent", prompt="Review PR #456: new ICMS_ST rule implementation")
Agent(subagent_type="core-infra-agent", prompt="Review PR #789: audit log middleware implementation")
```

### PO Coordination
```python
# Clarificar regras novas
Agent(subagent_type="po-scrum-agent", prompt="Validate new regulatory rules from PO documents for Card #16")

# Sprint planning
Agent(subagent_type="po-scrum-agent", prompt="Clarify acceptance criteria for Card #16 Rules DB-Driven")
```

---

## 📁 Agent File Locations

| Agent | File Path |
|-------|-----------|
| Tech Lead (Main) | `techlead-agent.md` |
| Backend Tech Lead | `agents/backend/techlead-backend-agent.md` |
| Core Agent | `agents/backend/core/core-agent.md` |
| Rules Engine Agent | `agents/backend/rules-engine/rules-engine-agent.md` |
| Integrations Agent | `agents/backend/integrations/integrations-agent.md` |
| Core Infra Agent | `agents/backend/core/core-infra-agent.md` |
| ML Agent | `agents/backend/ml/ml-agent.md` |
| Frontend UI Agent | `agents/frontend/ui/ui-agent.md` |
| Frontend Pages Agent | `agents/frontend/pages/pages-agent.md` |
| Frontend State Agent | `agents/frontend/state/state-agent.md` |
| Frontend Testing Agent | `agents/frontend/testing/testing-agent.md` |
| PO Scrum Agent | `po-scrum-agent.md` |

---

## 🚀 Quick Reference - Sprint 1 Commands

### Card #08: Documents Page
```python
# State hooks
Agent(subagent_type="frontend-state-agent", prompt="Create useDocuments hooks: list, detail, upload, reprocess with TanStack Query")

# UI components
Agent(subagent_type="frontend-ui-agent", prompt="Create UploadZone (react-dropzone), DocumentsTable, DocumentDetailModal for Documents page")

# Page implementation
Agent(subagent_type="frontend-pages-agent", prompt="Replace Documents ComingSoon with full implementation: upload, list, detail")

# Tests
Agent(subagent_type="frontend-testing-agent", prompt="Write full test suite for Documents page: components, hooks, integration")
```

### Card #09: Discrepancies Page
```python
Agent(subagent_type="frontend-state-agent", prompt="Create useDiscrepancies hooks: list with filters, summary, bulk status, review request")
Agent(subagent_type="frontend-ui-agent", prompt="Create FilterSidebar, BulkActionsToolbar, DiscrepancyDetailModal")
Agent(subagent_type="frontend-pages-agent", prompt="Replace Discrepancies ComingSoon with list, filters, detail, bulk actions")
Agent(subagent_type="frontend-testing-agent", prompt="Write full test suite for Discrepancies page")
```

### Card #10: Contests Page
```python
Agent(subagent_type="frontend-state-agent", prompt="Create useContests hooks: CRUD, send, negotiate, payments")
Agent(subagent_type="frontend-ui-agent", prompt="Create CreateContestWizard (multi-step), ContestDetailView, NegotiateModal, PaymentsTable")
Agent(subagent_type="frontend-pages-agent", prompt="Replace Contests ComingSoon with create, detail, negotiate, payments")
Agent(subagent_type="frontend-testing-agent", prompt="Write full test suite for Contests page")
```

### Backend Sprint 1
```python
# Rate Limiter + Rules Cache (core-infra)
Agent(subagent_type="backend-techlead-agent", prompt="Review PR: Rate Limiter Redis (slowapi) implementation - Card #04")
Agent(subagent_type="backend-techlead-agent", prompt="Review PR: Rules Engine Redis Cache implementation - Card #05")

# XML Parser (core)
Agent(subagent_type="backend-techlead-agent", prompt="Review PR: XML Parser namespace fix NF-e 4.00 - Card #12")

# NestJS Deprecation (techlead)
Agent(subagent_type="backend-techlead-agent", prompt="Review PR: Archive packages/backend (NestJS) - Card #06")
```

---

## ⚡ Usage Tips

1. **Sempre use `subagent_type` exato** conforme listado acima
2. **Prompt claro e específico** - descreva o que precisa, não como fazer
3. **Uma task por invocação** - evite prompts muito longos
4. **Aguarde o resultado** antes de invocar outro agente
5. **Para reviews**, sempre passe o PR number e descrição

---

*Atualizado: 2026-11-01 | Total: 12 agentes especializados + 2 tech leads*