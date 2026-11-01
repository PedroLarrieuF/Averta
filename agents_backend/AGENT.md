# AvertaSaaS Backend Agent - Entrypoint

> **Pasta**: `C:\Users\Pedro\Desktop\AvertaSaaS\agents_backend\`
> **Projeto**: AvertaSaaS - Freight Audit SaaS com success-fee billing
> **Stack**: FastAPI + Prisma Client Python + PostgreSQL + Redis/Celery + MinIO

---

## 🎯 Como Usar Este Agente

Quando precisar de tarefas de **backend**, invoque este agente com o contexto desta pasta. O agente já possui:

1. **Memória do projeto** (carregue `MEMORY.md` + arquivos `.md` em `memory/`)
2. **Contexto completo** da implementação de precificação progressiva
3. **Estrutura do código** mapeada

### Comando de Ativação Sugerido
```
"Atue como agente de backend do AvertaSaaS. Use a pasta agents_backend como contexto."
```

---

## 📁 Estrutura da Pasta

```
agents_backend/
├── AGENT.md                    # Este arquivo (entrypoint)
├── MEMORY.md                   # Índice de memórias
├── memory/
│   ├── avertasaas-project.md   # Contexto geral do projeto
│   └── avertasaas-progressive-pricing.md  # Implementação 5%/10%
└── (futuras memories aqui)
```

---

## 🧠 Memórias Carregadas (Resumo)

### 1. `avertasaas-project.md` - Projeto Base
- **Backend**: FastAPI 0.109, Prisma Client Python, PostgreSQL 16, Redis 7, Celery 5
- **25 Models Prisma**: Auth, Companies, Clients, Carriers, Contracts, Documents, Discrepancies, Contests, Reports, Notifications
- **Rules Engine v2**: 17 regras (ICMS, Frete, Redespacho, Pedágio, Ad Valorem, GRIS, SICOBAN, CT-e Complementar)
- **API Prefix**: `/api/v1`
- **Dev**: `cd backend && poetry run start` (porta 8000)

### 2. `avertasaas-progressive-pricing.md` - Precificação Progressiva ✨ **NOVA**
- **Regra**: Mês 1 = 5% | Mês 2+ = 10% sobre valores recuperados
- **Campos em Contract**: `pricingModel`, `progressiveStartDate`, `progressiveMonth1Pct`, `progressiveMonth2Pct`
- **Core Logic**: `ContractsService.calculate_progressive_fee_pct()`
- **Integração**: Contests (create/respond), Reports, Celery task diária
- **Endpoint**: `POST /api/v1/contests/{id}/recalculate-fee`

---

## 🔑 Padrões de Código do Projeto

| Padrão | Descrição |
|--------|-----------|
| **BaseService** | CRUD padronizado em `app/modules/base.py` |
| **Dependencies** | `CompanyIdDep`, `PaginationDep`, `CurrentUserDep`, roles (`RequireAdmin`, `RequireManager`, `RequireAuditor`) |
| **Exceptions** | Hierarquia em `app/core/exceptions.py` (`NotFoundError`, `ConflictError`, `BadRequestError`, `ForbiddenError`) |
| **Structlog** | JSON logging em todos módulos |
| **Prisma** | `interface = "asyncio"`, tipos recursivos depth 5 |
| **Enums** | String enums no Prisma, validação Pydantic com `pattern` |

---

## 🚀 Tarefas Típicas para Este Agente

- [ ] Novo endpoint / módulo CRUD
- [ ] Nova regra no Rules Engine v2
- [ ] Otimização de query Prisma / índice
- [ ] Task Celery / Beat schedule
- [ ] Correção de bug em processamento XML/CT-e
- [ ] Relatório / export novo
- [ ] Migração de schema Prisma
- [ ] Testes (pytest-asyncio + coverage)

---

## ⚡ Quick Start para Nova Sessão

```bash
# 1. Ler memórias
cat agents_backend/MEMORY.md
cat agents_backend/memory/avertasaas-project.md
cat agents_backend/memory/avertasaas-progressive-pricing.md

# 2. Verificar schema atual
cat ../backend/prisma/schema.prisma

# 3. Rodar backend (se necessário)
cd ../backend && poetry run start
```

---

## 📝 Atualização Contínua

**Após cada tarefa completa**, atualize:
1. `MEMORY.md` - adicione nova memory se relevante
2. Crie novo `.md` em `memory/` para features complexas
3. Mantenha este `AGENT.md` atualizado com novos padrões/endpoints

---

*Última atualização: 2026-11-01 — Implementação precificação progressiva (5%/10%)*