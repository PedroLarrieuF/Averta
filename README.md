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
│  │   Vite +     │     │   Prisma)    │     │   16 +       │               │
│  │   Tailwind)  │     │              │     │   PgBouncer) │               │
│  └──────────────┘     └──────┬───────┘     └──────────────┘               │
│                              │                                            │
│         ┌────────────────────┼────────────────────┐                       │
│         ▼                    ▼                    ▼                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│  │    REDIS    │     │   MINIO     │     │   CELERY    │                │
│  │  (Cache +   │     │   (S3/      │     │  (Workers + │                │
│  │   Broker)   │     │   Storage)  │     │   Beat)     │                │
│  └─────────────┘     └─────────────┘     └─────────────┘                │
│         │                                       │                        │
│         └───────────────────────────────────────┘                        │
│                              │                                            │
│                              ▼                                            │
│                     ┌───────────────┐                                    │
│                     │   FLOWER      │                                    │
│                     │ (Monitoring)  │                                    │
│                     └───────────────┘                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| **Frontend** | React 18 + Vite + TypeScript + TailwindCSS | Latest |
| **Backend** | FastAPI 0.109 (async) + Prisma Client Python | Latest |
| **Database** | PostgreSQL 16 + PgBouncer (connection pooling) | 16-alpine |
| **Cache/Queue** | Redis 7 + Celery 5 (workers + beat + flower) | 7-alpine |
| **Storage** | MinIO (S3-compatible) | Latest |
| **Email** | SendGrid (templates Jinja2) | - |
| **Auth** | JWT (access 15min + refresh 7d) + RBAC | - |
| **Multi-tenancy** | Isolamento por `company_id` em todos os models | - |

---

## 📋 Pré-requisitos

- **Docker** ≥ 24.0 e **Docker Compose** ≥ 2.20
- **Node.js** ≥ 20.0 (para frontend local)
- **pnpm** ≥ 9.0 (package manager)
- **Python** ≥ 3.11 + **Poetry** (para backend local)
- **Git**
- **OpenSSL** (para gerar chaves JWT)

> **Nota**: Para desenvolvimento local completo, recomenda-se usar **Docker Compose** que sobe toda a stack (PostgreSQL, Redis, MinIO, Backend, Celery, Flower). Frontend pode rodar fora do Docker para hot-reload mais rápido.

---

## 🚀 Quick Start (Docker Compose - Recomendado)

### 1. Clone e configure variáveis de ambiente

```bash
cd D:/Averta
git clone <repo-url> .  # se ainda não clonado

# Backend
cd backend
cp .env.example .env
# Edite .env com suas chaves (JWT_SECRET_KEY, SENDGRID_API_KEY, etc.)
# Dica: Gere chaves JWT com: openssl rand -base64 32

# Voltar para raiz
cd ..
```

### 2. Suba toda a stack (Backend + Infra)

```bash
cd backend
docker compose up -d --build
```

**Serviços iniciados:**
| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **PostgreSQL** | 5432 | Database principal |
| **PgBouncer** | 6432 | Connection pooler (transaction mode) |
| **Redis** | 6379 | Cache + Celery broker |
| **MinIO** | 9000/9001 | S3 storage + Console |
| **Backend API** | 8000 | FastAPI (Swagger: http://localhost:8000/docs) |
| **Celery Worker** | - | Processamento assíncrono (4 concorrentes) |
| **Celery Beat** | - | Agendador de tarefas periódicas |
| **Flower** | 5555 | Monitoramento Celery (http://localhost:5555) |

### 3. Inicialize o banco de dados

```bash
# Gere o Prisma Client
docker compose exec backend poetry run prisma generate

# Aplique migrations (cria tabelas + seed data)
docker compose exec backend poetry run prisma migrate deploy

# OU para desenvolvimento (push schema sem migrations)
# docker compose exec backend poetry run prisma db push
```

### 4. Suba o Frontend (em outro terminal)

```bash
cd D:/Averta/frontend
pnpm install
pnpm dev
```

**Frontend disponível em:** http://localhost:3000 (Vite dev server)

> **Nota**: O Vite proxy está configurado para encaminhar `/api` → `http://localhost:8000`. Verifique `vite.config.ts` (porta 3000).

---

## 🔧 Desenvolvimento Local (Sem Docker para Backend)

### Backend (Poetry)

```bash
cd D:/Averta/backend

# Instale dependências
poetry install --with dev

# Configure .env local (DATABASE_URL para localhost:5432, REDIS_URL para localhost:6379)
cp .env.example .env
# Edite DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
# Edite REDIS_URL=redis://localhost:6379/0

# Gere Prisma Client
poetry run prisma generate

# Crie banco e aplique migrations
poetry run prisma migrate dev  # Cria migration + aplica
# OU para apenas aplicar existentes:
poetry run prisma migrate deploy

# Rode a API (com hot-reload)
poetry run start
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Em terminais separados:
poetry run worker    # celery -A app.core.celery_app worker --loglevel=info --concurrency=4
poetry run beat      # celery -A app.core.celery_app beat --loglevel=info
```

### Frontend (Vite)

```bash
cd D:/Averta/frontend
pnpm install
pnpm dev
```

---

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

### Backend (Docker Multi-stage + Distroless)

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

### Frontend

```bash
cd D:/Averta/frontend

# Build production
pnpm build

# Preview local do build
pnpm preview
```

### Stack Produção (Docker Compose)

```bash
cd D:/Averta/backend

# Valida configuração produção
docker compose -f docker-compose.yml -f docker-compose.prod.yml config

# Sobe stack produção
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Para stack produção
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

**Diferenças `docker-compose.prod.yml`:**
- Resource limits (CPU/Memory) por serviço
- Restart policies `unless-stopped`
- JSON-file logging com rotação (max-size: 10m, max-file: 3-5)
- Read-only root filesystem
- Dropped ALL capabilities
- Security opt: `no-new-privileges`
- tmpfs para diretórios graváveis
- Réplicas para celery-worker (2x)
- Rede dedicada subnet `172.28.0.0/16`

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

# Database (Docker Compose usa pgbouncer:6432)
DATABASE_URL=postgresql://postgres:postgres@pgbouncer:6432/averta
DATABASE_READ_REPLICA_URL=postgresql://postgres:postgres@postgres:5432/averta
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis:6379/0

# JWT (GERAR COM: openssl rand -base64 32)
JWT_SECRET_KEY=<32+ chars>
JWT_REFRESH_SECRET_KEY=<32+ chars>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true

# S3/MinIO
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=averta-documents
S3_REGION=us-east-1
S3_PUBLIC_URL=http://localhost:9000

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

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
| **Flower (Celery)** | http://localhost:5555 | - |
| **Prisma Studio** | http://localhost:5555 | (quando rodando `prisma studio`) |
| **PostgreSQL** | localhost:5432 | postgres / postgres / averta |
| **PgBouncer** | localhost:6432 | postgres / postgres / averta |
| **Redis** | localhost:6379 | - |
| **Mailhog (Email UI)** | http://localhost:8025 | - |

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

### Docker Compose (Backend Stack)

```bash
cd D:/Averta/backend

# Subir tudo
docker compose up -d

# Ver logs
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f postgres

# Reiniciar apenas backend
docker compose restart backend

# Rebuild backend após mudanças no Dockerfile/pyproject.toml
docker compose up -d --build backend

# Parar tudo (mantém volumes)
docker compose down

# Parar tudo + REMOVER volumes (CUIDADO: apaga dados do banco!)
docker compose down -v

# Entrar no container backend (apenas dev - distroless não tem shell)
docker compose exec backend bash  # só funciona no dev (não distroless)

# Ver status containers
docker compose ps
```

### Banco de Dados

```bash
# Prisma Studio (UI)
docker compose exec backend poetry run prisma studio

# Migration status
docker compose exec backend poetry run prisma migrate status

# Nova migration
docker compose exec backend poetry run prisma migrate dev --name add_campo_x

# Aplicar migrations pendentes (prod)
docker compose exec backend poetry run prisma migrate deploy

# Reset DB (DEV ONLY)
docker compose exec backend poetry run prisma migrate reset --force

# Seed
docker compose exec backend poetry run db-seed
```

### Celery / Tasks

```bash
# Ver tasks ativas (Flower)
# Acesse: http://localhost:5555

# Ou via CLI
docker compose exec backend poetry run celery -A app.core.celery_app inspect active
docker compose exec backend poetry run celery -A app.core.celery_app inspect scheduled
docker compose exec backend poetry run celery -A app.core.celery_app inspect stats

# Purge queue (CUIDADO)
docker compose exec backend poetry run celery -A app.core.celery_app purge
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
# 1. Verifique se postgres está healthy
docker compose ps
docker compose logs postgres

# 2. Verifique se pgbouncer subiu após postgres
docker compose logs pgbouncer

# 3. Teste conexão manual
docker compose exec postgres pg_isready -U postgres

# 4. Se pgbouncer falhar, tente conectar direto no postgres (porta 5432)
# Edite .env: DATABASE_URL=postgresql://postgres:postgres@postgres:5432/averta
```

### Prisma Client não gerado / Erro "PrismaClientKnownRequestError"

```bash
cd D:/Averta/backend
docker compose exec backend poetry run prisma generate
# Se persistir:
docker compose exec backend rm -rf node_modules/.prisma
docker compose exec backend poetry run prisma generate
```

### Migration falha / Schema drift

```bash
# Ver diff
docker compose exec backend poetry run prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script

# Reset completo (DEV ONLY - apaga dados!)
docker compose exec backend poetry run prisma migrate reset --force
docker compose exec backend poetry run prisma migrate dev
```

### Frontend não conecta na API

```bash
# 1. Verifique vite.config.ts - proxy para /api
# 2. Verifique CORS_ORIGINS no backend .env inclui http://localhost:5173
# 3. Verifique se backend está rodando na porta 8000
curl http://localhost:8000/health
```

### Celery tasks não executam

```bash
# 1. Verifique Redis
docker compose logs redis
docker compose exec redis redis-cli ping

# 2. Verifique worker logs
docker compose logs celery-worker

# 3. Verifique Flower
# http://localhost:5555

# 4. Teste task manual
docker compose exec backend poetry run python -c "
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
├── backend/                    # FastAPI + Prisma + Celery
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
│   ├── Dockerfile              # Multi-stage (builder + distroless runtime)
│   ├── docker-compose.yml      # Dev stack (8 services)
│   ├── docker-compose.prod.yml # Production overrides
│   ├── pyproject.toml          # Poetry deps + scripts
│   └── .env.example
├── frontend/                   # React 18 + Vite + Tailwind
│   ├── src/
│   │   ├── components/         # 50+ componentes UI (Radix + Tailwind)
│   │   ├── pages/              # 30+ páginas (Dashboard, Documents, Discrepancies, Contests, Contracts, Reports, Settings)
│   │   ├── hooks/              # Custom hooks
│   │   ├── services/           # Axios API client + TanStack Query
│   │   └── contexts/           # AuthContext, etc.
│   ├── package.json            # pnpm + Vite + Vitest
│   ├── tailwind.config.js
│   └── vite.config.ts          # Proxy /api → localhost:8000
├── docker-compose.yml          # Root compose (infra only: postgres, redis, minio, mailhog)
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