# Averta SaaS - Freight Audit Platform

> **Auditoria de Frete com Cobrança por Êxito** — Plataforma completa B2B para auditoria automatizada de CT-e/NF-e com modelo de **success-fee (cobrança por êxito)**.

---

## 🏗 Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AVERTA SAAS PLATFORM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│  │   FRONTEND   │────▶│   BACKEND    │────▶│  DATABASE    │               │
│  │   (React +   │     │  (FastAPI +  │     │  (PostgreSQL │               │
│  │   Vite +     │     │   Prisma)    │     │   16)        │               │
│  │   Tailwind)  │     │              │     │              │               │
│  │   Port 3000  │     │   Port 8000  │     │   Port 5432  │               │
│  └──────────────┘     └──────┬───────┘     └──────────────┘               │
│                              │                                            │
│         ┌────────────────────┼────────────────────┐                       │
│         ▼                    ▼                    ▼                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│  │    REDIS    │     │   MINIO     │     │   CELERY    │                │
│  │  (Cache +   │     │   (S3/      │     │  (Workers + │                │
│  │   Broker)   │     │   Storage)  │     │   Beat)     │                │
│  │   Port 6379 │     │   Port 9000 │     │   Local     │                │
│  └─────────────┘     └─────────────┘     └─────────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

| Camada | Tecnologia | Versão | Porta |
|--------|------------|--------|-------|
| **Frontend** | React 18 + Vite + TypeScript + TailwindCSS | Latest | 3000 |
| **Backend** | FastAPI 0.109 (async) + Prisma Client Python | Latest | 8000 |
| **Database** | PostgreSQL 16 (Docker) | 16-alpine | 5432 |
| **Cache/Queue** | Redis 7 (Docker) + Celery 5 (Local) | 7-alpine | 6379 |
| **Storage** | MinIO (Docker, S3-compatible) | Latest | 9000/9001 |
| **Email** | SendGrid (templates Jinja2) | - | - |
| **Auth** | JWT (access 15min + refresh 7d) + RBAC | - | - |
| **Multi-tenancy** | Isolamento por `company_id` em todos os models | - | - |

> **Arquitetura Híbrida**: Infraestrutura (PostgreSQL, Redis, MinIO) roda em **Docker**. Aplicação (Frontend + Backend + Celery) roda **localmente** (Poetry/Vite) para desenvolvimento mais rápido, hot-reload nativo e debugging simplificado.

---

## 📋 Pré-requisitos

- **Docker** ≥ 24.0 e **Docker Compose** ≥ 2.20 (apenas para infraestrutura)
- **Node.js** ≥ 20.0
- **pnpm** ≥ 9.0 (package manager)
- **Python** ≥ 3.11 + **Poetry**
- **Git**
- **OpenSSL** (para gerar chaves JWT)

---

## 🚀 Quick Start (Infra Docker + App Local - Recomendado)

### 1. Clone e configure variáveis de ambiente

```bash
cd D:/Averta
git clone <repo-url> .  # se ainda não clonado

# Backend
cd backend
cp .env.example .env
# Edite .env com suas chaves (JWT_SECRET_KEY, SENDGRID_API_KEY, etc.)
# IMPORTANTE: Use localhost para serviços Docker:
#   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
#   REDIS_URL=redis://localhost:6379/0
#   S3_ENDPOINT=http://localhost:9000
# Dica: Gere chaves JWT com: openssl rand -base64 32

# Voltar para raiz
cd ..
```

### 2. Suba apenas a infraestrutura (PostgreSQL, Redis, MinIO, Mailhog)

```bash
# Na raiz do projeto
docker compose up -d
```

**Serviços de infraestrutura iniciados:**
| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **PostgreSQL** | 5432 | Database principal (dados persistem em volume) |
| **Redis** | 6379 | Cache + Celery broker |
| **MinIO** | 9000/9001 | S3 storage + Console (minioadmin/minioadmin) |
| **Mailhog** | 1025/8025 | SMTP testing + Web UI |

> **Nota**: O banco de dados **já vem populado** com seed data (empresas, usuários, regras, etc.). Não execute `prisma migrate reset` a menos que queira apagar tudo.

### 3. Inicialize o Backend (Terminal 1)

```bash
cd D:/Averta/backend

# Instale dependências (apenas primeira vez)
poetry install --with dev

# Gere Prisma Client
poetry run prisma generate

# Aplique migrations (já existem, apenas aplica)
poetry run prisma migrate deploy

# Rode a API com hot-reload (porta 8000)
poetry run start
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend API disponível em:** http://localhost:8000  
**Swagger Docs:** http://localhost:8000/docs

### 4. Inicialize Celery Worker + Beat (Terminal 2 e 3)

```bash
# Terminal 2 - Worker
cd D:/Averta/backend
poetry run worker
# celery -A app.core.celery_app worker --loglevel=info --concurrency=4

# Terminal 3 - Beat (scheduler)
cd D:/Averta/backend
poetry run beat
# celery -A app.core.celery_app beat --loglevel=info
```

### 5. Inicialize o Frontend (Terminal 4)

```bash
cd D:/Averta/frontend

# Instale dependências (apenas primeira vez)
pnpm install

# Rode o Vite dev server (porta 3000)
pnpm dev
```

**Frontend disponível em:** http://localhost:3000  
> O Vite proxy encaminha `/api` → `http://localhost:8000`. Verifique `vite.config.ts`.

---

## ⚡ Quick Start Automatizado (Script)

```bash
# Na raiz do projeto - sobe infra + backend + frontend em terminais separados
./scripts/quickstart.sh
```

> Veja seção **Quickstarter Script** abaixo para detalhes.

---

## 🔧 Desenvolvimento Local (Arquitetura Padrão)

Esta é a arquitetura recomendada: **Infra em Docker, App Local**.

### Backend (Poetry) - Porta 8000

```bash
cd D:/Averta/backend

# Instale dependências (apenas primeira vez)
poetry install --with dev

# Configure .env para localhost (infra roda em Docker nas portas padrão)
cp .env.example .env
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
# REDIS_URL=redis://localhost:6379/0
# S3_ENDPOINT=http://localhost:9000
# FRONTEND_URL=http://localhost:3000

# Gere Prisma Client
poetry run prisma generate

# Aplique migrations existentes (banco já populado)
poetry run prisma migrate deploy

# Rode a API com hot-reload (porta 8000)
poetry run start
```

### Celery Worker + Beat (Terminais Separados)

```bash
# Terminal Worker - processa tasks assíncronas
cd D:/Averta/backend
poetry run worker

# Terminal Beat - agendador de tarefas periódicas
cd D:/Averta/backend
poetry run beat

# Opcional: Flower monitoring (porta 5555)
cd D:/Averta/backend
poetry run flower
```

### Frontend (Vite) - Porta 3000

```bash
cd D:/Averta/frontend
pnpm install
pnpm dev
```

---

## 🗄️ Banco de Dados - Comandos Úteis

O banco **já vem populado** com seed data via Docker volume. Use estes comandos para gerenciar:

```bash
# Via Poetry (backend local conectando no PostgreSQL Docker)
cd D:/Averta/backend

# Prisma Studio (UI visual do banco) - porta 5555
poetry run prisma studio

# Ver status das migrations
poetry run prisma migrate status

# Criar nova migration (após editar schema.prisma)
poetry run prisma migrate dev --name <nome>

# Reset completo (CUIDADO: apaga dados! Use apenas se necessário)
poetry run prisma migrate reset --force

# Seed data (dados de desenvolvimento)
poetry run db-seed

# Backup manual (direto no container PostgreSQL)
docker compose exec postgres pg_dump -U postgres averta > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U postgres averta < backup_20240115.sql

# Acessar psql direto
docker compose exec postgres psql -U postgres -d averta
```

### Prisma Schema Location
- **Schema**: `backend/prisma/schema.prisma` (25+ models, 100+ fields)
- **Migrations**: `backend/prisma/migrations/` (15+ arquivos)
- **Seed**: `backend/prisma/seed.ts` (TypeScript) + `backend/scripts/seed.py` (Python)

## 🗄️ Banco de Dados - Comandos Úteis

```bash
# Via Docker (backend container)
cd D:/Averta/backend

# Prisma Studio (UI visual do banco)
docker compose exec backend poetry run prisma studio
# Acesse: http://localhost:5555

# Ver status das migrations
docker compose exec backend poetry run prisma migrate status

# Criar nova migration
docker compose exec backend poetry run prisma migrate dev --name <nome>

# Reset completo (CUIDADO: apaga dados!)
docker compose exec backend poetry run prisma migrate reset --force

# Seed data (dados de desenvolvimento)
docker compose exec backend poetry run db-seed

# Backup manual
docker compose exec postgres pg_dump -U postgres averta > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U postgres averta < backup_20240115.sql

# Acessar psql direto
docker compose exec postgres psql -U postgres -d averta
```

### Prisma Schema Location
- **Schema**: `backend/prisma/schema.prisma` (25+ models, 100+ fields)
- **Migrations**: `backend/prisma/migrations/` (15+ arquivos)
- **Seed**: `backend/prisma/seed.ts` (TypeScript) + `backend/scripts/seed.py` (Python)

---

## 🧪 Testes

### Backend

```bash
cd D:/Averta/backend

# Todos os testes com cobertura
poetry run test-cov

# Apenas rules engine (rápido, ~50 testes)
poetry run pytest tests/test_rules_critical.py -v

# Por marcadores
poetry run pytest -m "unit" -v
poetry run pytest -m "integration" -v

# Testes específicos
poetry run pytest tests/test_rules_critical.py::test_icms_diferential_triggered -v
poetry run pytest tests/test_rules_critical.py::test_full_audit -v
```

**Cobertura atual**: ~78% (rules engine, services, parsers)

### Frontend

```bash
cd D:/Averta/frontend

# Testes unitários
pnpm test

# Com UI
pnpm test:ui

# Com cobertura
pnpm test:coverage
```

---

## 📦 Build de Produção

### Backend (Docker Multi-stage + Distroless - Apenas Produção)

```bash
cd D:/Averta/backend

# Build da imagem production (distroless, non-root, <200MB)
docker build -t averta/backend:latest .

# Build multi-arch (amd64 + arm64)
docker buildx build --platform linux/amd64,linux/arm64 -t averta/backend:latest --push .

# Security scan (Trivy)
trivy image averta/backend:latest --severity HIGH,CRITICAL

# SBOM (Syft)
syft averta/backend:latest -o spdx-json=sbom.spdx.json

# Assinar SBOM (cosign keyless)
cosign sign-blob --yes sbom.spdx.json
```

> **Nota**: Em desenvolvimento, **não use Docker para o backend**. Rode localmente com `poetry run start` para hot-reload nativo e debugging simplificado.

### Frontend

```bash
cd D:/Averta/frontend

# Build production
pnpm build

# Preview local do build
pnpm preview
```

### Stack Produção (Kubernetes / Docker Swarm)

Em produção, use Kubernetes (Helm) ou Docker Swarm com as imagens construídas acima. O `docker-compose.prod.yml` foi descontinuado para desenvolvimento local.

**Diferenças Produção vs Desenvolvimento:**
- Resource limits (CPU/Memory) por serviço
- Restart policies `unless-stopped`
- JSON-file logging com rotação
- Read-only root filesystem
- Dropped ALL capabilities
- Security opt: `no-new-privileges`
- Réplicas para celery-worker
- Rede dedicada com subnet isolada

---

## 🔐 Variáveis de Ambiente Obrigatórias

### Backend (`.env`)

```bash
# Application
APP_NAME="Averta SaaS"
DEBUG=true
ENVIRONMENT=development
API_PREFIX="/api/v1"

# Server
HOST=0.0.0.0
PORT=8000

# Database (Infra Docker roda em localhost:5432)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
DATABASE_READ_REPLICA_URL=postgresql://postgres:postgres@localhost:5432/averta
DATABASE_POOL_SIZE=20

# Redis (Infra Docker roda em localhost:6379)
REDIS_URL=redis://localhost:6379/0

# JWT (GERAR COM: openssl rand -base64 32)
JWT_SECRET_KEY=<32+ chars>
JWT_REFRESH_SECRET_KEY=<32+ chars>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true

# S3/MinIO (Infra Docker roda em localhost:9000)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=averta-documents
S3_REGION=us-east-1
S3_PUBLIC_URL=http://localhost:9000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Email (SendGrid preferido)
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@averta.com
SENDGRID_FROM_NAME="Averta Auditoria"

# Frontend URL (para links em emails)
FRONTEND_URL=http://localhost:3000

# Success Fee
SUCCESS_FEE_PERCENTAGE=20.0

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Frontend (`.env` - opcional)

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
```

---

## 🌐 URLs de Acesso (Local Development)

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Frontend (Vite)** | http://localhost:3000 | - |
| **Backend API (Swagger)** | http://localhost:8000/docs | - |
| **Backend Health** | http://localhost:8000/health | - |
| **Backend OpenAPI** | http://localhost:8000/api/v1/openapi.json | - |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **Flower (Celery)** | http://localhost:5555 | - (rode `poetry run flower`) |
| **Prisma Studio** | http://localhost:5555 | (rode `poetry run prisma studio`) |
| **PostgreSQL** | localhost:5432 | postgres / postgres / averta |
| **Redis** | localhost:6379 | - |
| **Mailhog (Email UI)** | http://localhost:8025 | - |

---

---

## 🔄 Fluxo de Trabalho Comum

### 1. Nova Feature (Backend)

```bash
cd D:/Averta/backend

# 1. Crie branch
git checkout -b feat/nova-funcionalidade

# 2. Desenvolva (API roda em hot-reload via docker compose)
# Edit: app/modules/<modulo>/...

# 3. Se mudou schema Prisma:
#    - Edite prisma/schema.prisma
#    - docker compose exec backend poetry run prisma migrate dev --name <descricao>
#    - docker compose exec backend poetry run prisma generate

# 4. Testes
poetry run test-cov

# 5. Lint/Type-check
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy app

# 6. Commit + Push
git add .
git commit -m "feat: descrição da feature"
git push origin feat/nova-funcionalidade
```

### 2. Nova Feature (Frontend)

```bash
cd D:/Averta/frontend

# 1. Crie branch
git checkout -b feat/nova-funcionalidade-frontend

# 2. Desenvolva (hot-reload ativo)
# Edit: src/pages/, src/components/, etc.

# 3. Testes
pnpm test
pnpm test:coverage

# 4. Lint
pnpm lint

# 5. Build check
pnpm build

# 6. Commit + Push
git add .
git commit -m "feat(frontend): descrição da feature"
git push origin feat/nova-funcionalidade-frontend
```

---

## 🛠 Comandos Úteis Diários

### Infraestrutura (Docker Compose - Raiz do Projeto)

```bash
cd D:/Averta

# Subir infra (PostgreSQL, Redis, MinIO, Mailhog)
docker compose up -d

# Ver logs
docker compose logs -f postgres
docker compose logs -f redis
docker compose logs -f minio

# Parar infra (mantém volumes - dados persistem)
docker compose down

# Parar infra + REMOVER volumes (CUIDADO: apaga dados do banco!)
docker compose down -v

# Ver status containers
docker compose ps
```

### Backend Local (Poetry)

```bash
cd D:/Averta/backend

# Rodar API (já em hot-reload via poetry run start)
poetry run start

# Worker Celery
poetry run worker

# Beat Celery
poetry run beat

# Flower monitoring
poetry run flower

# Lint/Type-check
poetry run lint
poetry run typecheck
poetry run format

# Testes
poetry run test-cov
```

### Banco de Dados (Via Poetry Local)

```bash
cd D:/Averta/backend

# Prisma Studio (UI) - porta 5555
poetry run prisma studio

# Migration status
poetry run prisma migrate status

# Nova migration (após editar schema.prisma)
poetry run prisma migrate dev --name add_campo_x

# Aplicar migrations pendentes
poetry run prisma migrate deploy

# Reset DB (DEV ONLY - CUIDADO: apaga dados!)
poetry run prisma migrate reset --force

# Seed data
poetry run db-seed
```

### Celery / Tasks (Via Poetry Local)

```bash
cd D:/Averta/backend

# Ver tasks ativas (Flower)
# Rode: poetry run flower
# Acesse: http://localhost:5555

# Ou via CLI
poetry run celery -A app.core.celery_app inspect active
poetry run celery -A app.core.celery_app inspect scheduled
poetry run celery -A app.core.celery_app inspect stats

# Purge queue (CUIDADO)
poetry run celery -A app.core.celery_app purge
```

### MinIO / Storage

```bash
# MinIO Console: http://localhost:9001
# User: minioadmin / Pass: minioadmin

# Via CLI (mc - MinIO Client)
docker run --rm -it --network averta-network minio/mc alias set local http://minio:9000 minioadmin minioadmin
docker run --rm -it --network averta-network minio/mc ls local/averta-documents
docker run --rm -it --network averta-network minio/mc cp local/averta-documents/arquivo.xml .
```

---

## 🐛 Troubleshooting Comum

### Backend não sobe / Erro de conexão DB

```bash
# 1. Verifique se infra Docker está rodando
cd D:/Averta
docker compose ps
docker compose logs postgres

# 2. Teste conexão manual no PostgreSQL Docker
docker compose exec postgres pg_isready -U postgres

# 3. Verifique .env do backend - deve apontar para localhost
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
# REDIS_URL=redis://localhost:6379/0
```

### Prisma Client não gerado / Erro "PrismaClientKnownRequestError"

```bash
cd D:/Averta/backend
poetry run prisma generate
# Se persistir:
rm -rf node_modules/.prisma
poetry run prisma generate
```

### Migration falha / Schema drift

```bash
cd D:/Averta/backend

# Ver diff
poetry run prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script

# Reset completo (DEV ONLY - apaga dados!)
poetry run prisma migrate reset --force
poetry run prisma migrate dev
```

### Frontend não conecta na API

```bash
# 1. Verifique vite.config.ts - proxy para /api → localhost:8000
# 2. Verifique CORS_ORIGINS no backend .env inclui http://localhost:3000
# 3. Verifique se backend está rodando na porta 8000
curl http://localhost:8000/health
```

### Celery tasks não executam

```bash
# 1. Verifique Redis (Docker)
cd D:/Averta
docker compose logs redis
docker compose exec redis redis-cli ping

# 2. Verifique se worker está rodando (terminal separado)
cd D:/Averta/backend
poetry run worker

# 3. Verifique Flower (opcional)
poetry run flower
# http://localhost:5555

# 4. Teste task manual
cd D:/Averta/backend
poetry run python -c "
from app.tasks.documents import process_document
process_document.delay('doc-id-aqui')
"
```

### Porta já em uso

```bash
# Encontre processo na porta
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Mate o processo
taskkill /PID <pid> /F        # Windows
kill -9 <pid>                 # Linux/Mac
```

---

## 📁 Estrutura do Projeto (Resumo)

```
D:/Averta/
├── backend/                    # FastAPI + Prisma + Celery (roda LOCAL via Poetry)
│   ├── app/
│   │   ├── core/               # Config, DB, Security, Middleware, Celery
│   │   ├── modules/            # 11 feature modules (auth, users, companies, clients, carriers, branches, contracts, documents, discrepancies, contests, reports, notifications)
│   │   ├── services/           # Shared logic (xml_parser, rules_engine_v2, pdf_generator, storage, email)
│   │   ├── tasks/              # Celery tasks (documents, discrepancies)
│   │   ├── templates/emails/   # 7 templates Jinja2
│   │   └── data/               # Static reference data (icms_rules.json, sicoban_table.json)
│   ├── prisma/
│   │   ├── schema.prisma       # 25 models + enums
│   │   ├── migrations/         # 15+ migrations
│   │   └── seed.ts             # Seed TypeScript
│   ├── tests/                  # pytest + pytest-asyncio (~78% coverage)
│   ├── Dockerfile              # Para produção apenas (multi-stage distroless)
│   ├── docker-compose.yml      # [LEGACY] Dev stack completo - NÃO USE para dev
│   ├── docker-compose.prod.yml # [LEGACY] Production - NÃO USE para dev
│   ├── pyproject.toml          # Poetry deps + scripts
│   └── .env.example
├── frontend/                   # React 18 + Vite + Tailwind (roda LOCAL via pnpm)
│   ├── src/
│   │   ├── components/         # 50+ componentes UI (Radix + Tailwind)
│   │   ├── pages/              # 30+ páginas (Dashboard, Documents, Discrepancies, Contests, Contracts, Reports, Settings)
│   │   ├── hooks/              # Custom hooks
│   │   ├── services/           # Axios API client + TanStack Query
│   │   └── contexts/           # AuthContext, etc.
│   ├── package.json            # pnpm + Vite + Vitest
│   ├── tailwind.config.js
│   └── vite.config.ts          # Proxy /api → localhost:8000
├── docker-compose.yml          # Infra apenas: postgres, redis, minio, mailhog
├── scripts/
│   └── quickstart.sh           # Script de inicialização automatizada
├── package.json                # Root workspace (turbo + pnpm)
├── pnpm-workspace.yaml
├── turbo.json                  # Turborepo config
└── .env.example                # Root env template
```

---

## 🔗 Links Úteis

- **Backend README detalhado**: `backend/README.md`
- **Infra Agent docs**: `agents-new/infra-agent/agent.md`
- **Tech Lead Review**: `agents-new/TECHLEAD_REVIEW.md`
- **API Docs (Swagger)**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
- **Flower (Celery)**: http://localhost:5555
- **Prisma Studio**: `poetry run prisma studio` → http://localhost:5555

---

## 📝 Licença

Proprietário — Averta SaaS. Uso interno apenas.

---

## 🤝 Contato

- **Tech Lead**: backend@averta.com.br
- **Slack**: #averta-backend
- **Confluence**: [Arquitetura & Decisões](https://averta.atlassian.net/wiki/spaces/BACK)

---

*Última atualização: 2026-11-10 — v1.0.0*