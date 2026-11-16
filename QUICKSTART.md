# Averta SaaS - Quickstart Guide

> **Complete setup guide for Local Development (Docker Infra + Local Apps) and Azure Deployment**

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Local Development Setup](#-local-development-setup-recommended)
3. [Azure Infrastructure Deployment](#-azure-infrastructure-deployment)
4. [Build & Deploy to Azure](#-build--deploy-to-azure)
5. [Daily Development Commands](#-daily-development-commands)
6. [Troubleshooting](#-troubleshooting)

---

## ✅ Prerequisites

| Tool | Version | Install Command |
|------|---------|-----------------|
| **Docker Desktop** | ≥ 24.0 | `winget install Docker.DockerDesktop` |
| **Node.js** | ≥ 20.0 | `winget install OpenJS.NodeJS.LTS` |
| **pnpm** | ≥ 9.0 | `npm install -g pnpm` |
| **Python** | ≥ 3.11 | `winget install Python.Python.3.12` |
| **Poetry** | Latest | `pipx install poetry` |
| **Git** | Latest | `winget install Git.Git` |
| **Azure CLI** | ≥ 2.55 | `winget install Microsoft.AzureCLI` |
| **Bicep CLI** | Latest | `az bicep install` |
| **OpenSSL** | Latest | Built-in Windows / `winget install OpenSSL.OpenSSL` |

> **Windows Users**: Run PowerShell as Administrator for winget commands.

---

## 🚀 Local Development Setup (Recommended)

### Architecture: **Docker Infrastructure + Local Applications**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  FRONTEND   │    │  BACKEND    │    │  CELERY     │        │
│   │  (Vite +    │    │  (Poetry +  │    │  (Worker +  │        │
│   │   React)    │    │   FastAPI)  │    │   Beat)     │        │
│   │  Port 3000  │    │  Port 8000  │    │  Local      │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                  │               │
│          └──────────────────┼──────────────────┘               │
│                             ▼                                  │
│   ┌─────────────────────────────────────────┐                 │
│   │        DOCKER INFRASTRUCTURE            │                 │
│   │  ┌─────────┐ ┌─────┐ ┌──────┐ ┌──────┐ │                 │
│   │  │PostgreSQL│ │Redis│ │MinIO │ │Mailhog│ │                 │
│   │  │  5432   │ │6379 │ │9000/1│ │1025/25│ │                 │
│   │  └─────────┘ └─────┘ └──────┘ └──────┘ │                 │
│   └─────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 1. Clone Repository

```bash
# Navigate to workspace
cd D:/Averta

# If not cloned yet:
# git clone <repo-url> .
```

---

### 2. Environment Configuration

#### Backend (.env)

```bash
cd D:/Averta/backend

# Copy template
cp .env.example .env

# Edit .env with your values (IMPORTANT: use localhost for Docker services)
# Key variables to configure:
# JWT_SECRET_KEY=<generate with: openssl rand -base64 32>
# JWT_REFRESH_SECRET_KEY=<generate with: openssl rand -base64 32>
# SENDGRID_API_KEY=<your-sendgrid-key>  # optional for dev
# FRONTEND_URL=http://localhost:3000
```

**Required .env values for local development:**

```bash
# Database (PostgreSQL in Docker on localhost)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
DATABASE_READ_REPLICA_URL=postgresql://postgres:postgres@localhost:5432/averta

# Redis (Docker on localhost)
REDIS_URL=redis://localhost:6379/0

# S3/MinIO (Docker on localhost)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=averta-documents
S3_REGION=us-east-1
S3_PUBLIC_URL=http://localhost:9000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

#### Frontend (.env - optional)

```bash
cd D:/Averta/frontend

# Create .env if needed
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
EOF
```

---

### 3. Start Infrastructure (Docker)

```bash
# From project root
cd D:/Averta

# Start all infrastructure services
docker compose up -d

# Verify all services are healthy
docker compose ps

# Expected output - all services should show "healthy":
# NAME                    STATUS          PORTS
# averta-postgres         healthy         0.0.0.0:5432->5432/tcp
# averta-redis            healthy         0.0.0.0:6379->6379/tcp
# averta-minio            healthy         0.0.0.0:9000-9001->9000-9001/tcp
# averta-mailhog          running         0.0.0.0:1025->1025/tcp, 0.0.0.0:8025->8025/tcp
```

**Infrastructure Services:**

| Service | Port | URL | Credentials |
|---------|------|-----|-------------|
| PostgreSQL | 5432 | `postgresql://postgres:postgres@localhost:5432/averta` | postgres / postgres |
| Redis | 6379 | `redis://localhost:6379` | - |
| MinIO API | 9000 | `http://localhost:9000` | minioadmin / minioadmin |
| MinIO Console | 9001 | `http://localhost:9001` | minioadmin / minioadmin |
| Mailhog SMTP | 1025 | - | - |
| Mailhog UI | 8025 | `http://localhost:8025` | - |

> **Important**: Database comes pre-populated with seed data via Docker volume. Do NOT run `prisma migrate reset` unless you want to wipe all data.

---

### 4. Start Backend (Terminal 1)

```bash
cd D:/Averta/backend

# Install dependencies (first time only)
poetry install --with dev

# Generate Prisma Client
poetry run prisma generate

# Apply existing migrations (database already seeded)
poetry run prisma migrate deploy

# Start API with hot-reload (port 8000)
poetry run start
# OR: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Backend:**
```bash
# Health check
curl http://localhost:8000/health
# {"status":"healthy","version":"1.0.0","environment":"development"}

# Swagger Docs
open http://localhost:8000/docs
```

---

### 5. Start Celery Worker (Terminal 2)

```bash
cd D:/Averta/backend
poetry run worker
# celery -A app.core.celery_app worker --loglevel=info --concurrency=4
```

---

### 6. Start Celery Beat (Terminal 3)

```bash
cd D:/Averta/backend
poetry run beat
# celery -A app.core.celery_app beat --loglevel=info
```

---

### 7. Start Frontend (Terminal 4)

```bash
cd D:/Averta/frontend

# Install dependencies (first time only)
pnpm install

# Start Vite dev server (port 3000)
pnpm dev
```

**Verify Frontend:**
- Open: http://localhost:3000
- Vite proxy forwards `/api/*` → `http://localhost:8000/api/v1`

---

### 8. Optional: Start Flower Monitoring (Terminal 5)

```bash
cd D:/Averta/backend
poetry run flower
# Open: http://localhost:5555
```

---

### 🎯 Quick Verification Checklist

```bash
# All services running?
curl http://localhost:8000/health          # Backend API
curl http://localhost:3000                 # Frontend
curl http://localhost:9001                 # MinIO Console
curl http://localhost:8025                 # Mailhog UI
curl http://localhost:5555                 # Flower (if running)
docker compose exec postgres pg_isready -U postgres
docker compose exec redis redis-cli ping
```

---

## ☁️ Azure Infrastructure Deployment

### Architecture: **Azure Native Services**

```
┌─────────────────────────────────────────────────────────────────┐
│                      AZURE PRODUCTION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                                               │
│   │  Azure DNS  │  (averta.com.br)                              │
│   └──────┬──────┘                                               │
│          │                                                       │
│   ┌──────▼──────┐                                               │
│   │ Application │  (WAF + TLS Termination)                      │
│   │   Gateway   │                                               │
│   └──────┬──────┘                                               │
│          │                                                       │
│   ┌──────▼──────┬──────────┬──────────┐                         │
│   │  Container  │ Container │Container │  (Container Apps)      │
│   │   Apps Env  │  Apps     │  Apps    │                         │
│   │             │  Backend  │ Worker   │                         │
│   │             │           │ Beat     │                         │
│   └──────┬──────┴─────┬─────┴────┬────┘                         │
│          │            │          │                               │
│   ┌──────▼────┐ ┌──────▼───┐ ┌────▼────┐                        │
│   │PostgreSQL │ │  Azure  │ │  Blob   │  (PaaS Services)        │
│   │ Flexible  │ │  Cache  │ │ Storage │                         │
│   │  Server   │ │ for Redis│ │         │                         │
│   └───────────┘ └─────────┘ └─────────┘                         │
│                                                                 │
│   ┌─────────────────────────────────────────┐                   │
│   │         Key Vault (Secrets)             │                   │
│   │  + Application Insights + Log Analytics │                   │
│   └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

### Prerequisites for Azure

```bash
# 1. Login to Azure
az login --use-device-code

# 2. Set subscription
az account set --subscription <YOUR_SUBSCRIPTION_ID>

# 3. Verify Bicep is installed
az bicep version
# If not installed: az bicep install
```

---

### 1. Set Up Key Vault & Secrets (One-time per environment)

#### Staging

```powershell
# Run from project root
cd D:/Averta

# Staging - auto-generates secure keys if not provided
.\infra\azure\scripts\setup-keyvault.ps1 `
  -SubscriptionId "<SUBSCRIPTION_ID>" `
  -Environment staging

# Output will show:
# Key Vault Name: averta-kv-staging
# Key Vault URI: https://averta-kv-staging.vault.azure.net
# Secrets stored: pg-admin-password, redis-access-key, jwt-secret-key, etc.
```

#### Production (Requires Manual Approval)

```powershell
cd D:/Averta

.\infra\azure\scripts\setup-keyvault.ps1 `
  -SubscriptionId "<SUBSCRIPTION_ID>" `
  -Environment production

# For production, you'll be prompted for:
# - PostgreSQL admin password (or auto-generated)
# - Redis access key (or auto-generated)
# - JWT secrets (auto-generated)
# - SendGrid API key (optional)
# - SMTP password (optional)
```

---

### 2. Deploy Infrastructure

#### Staging

```powershell
cd D:/Averta

# Deploy staging infrastructure
.\infra\azure\scripts\deploy-staging.ps1 `
  -SubscriptionId "<SUBSCRIPTION_ID>"

# Options:
# -WhatIf          # Preview changes without deploying
# -Confirm:$false  # Skip confirmation prompt
```

#### Production (Requires Approver Email)

```powershell
cd D:/Averta

# Deploy production infrastructure (MANDATORY: approver email)
.\infra\azure\scripts\deploy-production.ps1 `
  -SubscriptionId "<SUBSCRIPTION_ID>" `
  -ApproverEmail "admin@averta.com.br"

# Options:
# -WhatIf          # Preview changes without deploying (recommended first)
# -SkipConfirmation # DANGEROUS: skips manual approval (not recommended)
```

---

### 3. Verify Deployment

```bash
# Check deployment outputs
az deployment group show \
  --resource-group rg-averta-staging \
  --name staging-deploy-<TIMESTAMP> \
  --query "properties.outputs" \
  -o table

# Key outputs to verify:
# - backendAppUrl: https://averta-backend-staging.xxx.azurecontainerapps.io
# - containerRegistryLoginServer: avertaacrstaging.azurecr.io
# - keyVaultUri: https://averta-kv-staging.vault.azure.net
# - appInsightsConnectionString: InstrumentationKey=xxx...
```

---

### 4. Configure GitHub Actions OIDC (One-time Setup)

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "github-actions-averta" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID> \
  --sdk-auth

# Configure OIDC federation (replace with your GitHub org/repo)
az ad app federated-credential create \
  --id <APP_ID_FROM_ABOVE> \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:PedroLarrieuF/Averta:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Add GitHub Repository Secrets:
# AZURE_CLIENT_ID = <appId from SP>
# AZURE_TENANT_ID = <tenantId from SP>
# AZURE_SUBSCRIPTION_ID = <subscriptionId>
```

---

## 🔨 Build & Deploy to Azure

### Backend Build (Docker)

```bash
cd D:/Averta/backend

# Build production image (multi-stage, hardened python:3.12-slim)
docker build -t averta/backend:latest .

# Build and push to Azure Container Registry
# First, login to ACR
az acr login --name avertaacrstaging  # or avertaacrproduction

# Tag and push
docker tag averta/backend:latest avertaacrstaging.azurecr.io/averta-backend:latest
docker push avertaacrstaging.azurecr.io/averta-backend:latest

# Multi-arch build (amd64 + arm64)
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t avertaacrstaging.azurecr.io/averta-backend:latest \
  --push .
```

### Frontend Build

```bash
cd D:/Averta/frontend

# Install dependencies
pnpm install

# Build production bundle
pnpm build

# Output in: dist/
# Deploy to Azure Static Web Apps or CDN
# (Configure in your CI/CD pipeline)
```

### Security Scanning (Recommended)

```bash
# Backend image scan
trivy image avertaacrstaging.azurecr.io/averta-backend:latest --severity HIGH,CRITICAL

# Generate SBOM
syft avertaacrstaging.azurecr.io/averta-backend:latest -o spdx-json=sbom.spdx.json

# Sign SBOM (cosign keyless)
cosign sign-blob --yes sbom.spdx.json
```

---

### Deploy via GitHub Actions (CI/CD)

The pipeline is defined in `.github/workflows/azure-deploy.yml`:

```bash
# Trigger staging deployment (manual)
gh workflow run azure-deploy.yml \
  -f environment=staging \
  -f action=apply

# Trigger production deployment (manual, requires approver)
gh workflow run azure-deploy.yml \
  -f environment=production \
  -f action=apply \
  -f approver="admin@averta.com.br"

# Run what-if analysis (preview changes)
gh workflow run azure-deploy.yml \
  -f environment=staging \
  -f action=plan
```

**Pipeline Features:**
- ✅ PR Validation: Bicep linting + what-if analysis
- ✅ Staging Deploy: Manual trigger
- ✅ Production Deploy: Manual + approver email required
- ✅ Weekly Drift Detection: Auto-creates GitHub issues

---

## 🛠 Daily Development Commands

### Infrastructure (Docker - Project Root)

```bash
cd D:/Averta

# Start infrastructure
docker compose up -d

# View logs
docker compose logs -f postgres
docker compose logs -f redis
docker compose logs -f minio

# Stop (keeps data)
docker compose down

# Stop + REMOVE VOLUMES (⚠️ DELETES DATABASE!)
docker compose down -v

# Restart specific service
docker compose restart postgres

# Check status
docker compose ps
```

### Backend (Poetry - D:/Averta/backend)

```bash
cd D:/Averta/backend

# Run API with hot-reload
poetry run start

# Celery Worker
poetry run worker

# Celery Beat
poetry run beat

# Flower Monitoring
poetry run flower

# Lint / Format / Type-check
poetry run lint        # ruff check
poetry run format      # ruff format
poetry run typecheck   # mypy

# Tests
poetry run test        # pytest
poetry run test-cov    # pytest with coverage
```

### Database (Prisma)

```bash
cd D:/Averta/backend

# Prisma Studio (visual DB browser)
poetry run prisma studio
# Open: http://localhost:5555

# Migration status
poetry run prisma migrate status

# Create new migration (after editing schema.prisma)
poetry run prisma migrate dev --name add_user_preferences

# Apply pending migrations
poetry run prisma migrate deploy

# Reset database (⚠️ DELETES ALL DATA!)
poetry run prisma migrate reset --force

# Seed development data
poetry run db-seed

# Backup
docker compose exec postgres pg_dump -U postgres averta > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U postgres averta < backup_20240115.sql
```

### Celery / Tasks

```bash
cd D:/Averta/backend

# Inspect active tasks
poetry run celery -A app.core.celery_app inspect active

# Inspect scheduled tasks
poetry run celery -A app.core.celery_app inspect scheduled

# Worker stats
poetry run celery -A app.core.celery_app inspect stats

# Purge queue (⚠️ DELETES ALL PENDING TASKS!)
poetry run celery -A app.core.celery_app purge
```

### Frontend (pnpm - D:/Averta/frontend)

```bash
cd D:/Averta/frontend

# Dev server with hot-reload
pnpm dev

# Build production
pnpm build

# Preview production build
pnpm preview

# Tests
pnpm test
pnpm test:ui
pnpm test:coverage

# Lint
pnpm lint
```

### MinIO / Storage (Local)

```bash
# MinIO Console: http://localhost:9001
# User: minioadmin / Pass: minioadmin

# MinIO Client (mc)
docker run --rm -it --network averta-network minio/mc alias set local http://minio:9000 minioadmin minioadmin
docker run --rm -it --network averta-network minio/mc ls local/averta-documents
docker run --rm -it --network averta-network minio/mc cp local/averta-documents/file.xml .
```

---

## 🔧 Azure-Specific Local Development (Azurite)

Use Azure Blob Storage emulator instead of MinIO:

```bash
# Start Azure-emulated infrastructure
cd D:/Averta
docker compose -f docker-compose.azure.yml --env-file .env.azure up -d

# Services:
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
# - Azurite (Blob): localhost:10000
# - Mailhog: localhost:8025/1025

# Backend uses .env.azure config:
# AZURE_STORAGE_ACCOUNT_NAME=devstoreaccount1
# AZURE_STORAGE_ACCOUNT_KEY=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==
# AZURE_STORAGE_ENDPOINT=http://azurite:10000/devstoreaccount1
```

---

## 🐛 Troubleshooting

### Backend Won't Start / DB Connection Error

```bash
# 1. Check Docker infrastructure
cd D:/Averta
docker compose ps
docker compose logs postgres

# 2. Test PostgreSQL connectivity
docker compose exec postgres pg_isready -U postgres

# 3. Verify backend .env uses localhost
grep DATABASE_URL D:/Averta/backend/.env
# Should be: postgresql://postgres:postgres@localhost:5432/averta
```

### Prisma Client Issues

```bash
cd D:/Averta/backend

# Regenerate Prisma Client
poetry run prisma generate

# If persistent issues
rm -rf node_modules/.prisma
poetry run prisma generate
```

### Migration Failures / Schema Drift

```bash
cd D:/Averta/backend

# View diff
poetry run prisma migrate diff \
  --from-empty \
  --to-schema-datamodel prisma/schema.prisma \
  --script

# Complete reset (⚠️ DELETES DATA - DEV ONLY!)
poetry run prisma migrate reset --force
poetry run prisma migrate dev
```

### Frontend Can't Connect to API

```bash
# 1. Check vite.config.ts proxy config
cat D:/Averta/frontend/vite.config.ts
# Should proxy /api → http://localhost:8000

# 2. Check CORS in backend .env
grep CORS_ORIGINS D:/Averta/backend/.env
# Should include: ["http://localhost:3000"]

# 3. Test backend directly
curl http://localhost:8000/health
```

### Celery Tasks Not Executing

```bash
# 1. Check Redis
cd D:/Averta
docker compose logs redis
docker compose exec redis redis-cli ping

# 2. Ensure worker is running (separate terminal)
cd D:/Averta/backend
poetry run worker

# 3. Test task manually
cd D:/Averta/backend
poetry run python -c "
from app.tasks.documents import process_document
process_document.delay('test-doc-id')
"
```

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :8000
kill -9 <pid>
```

### Azure Deployment Issues

```bash
# Check deployment status
az deployment group show \
  -g rg-averta-staging \
  -n staging-deploy-<TIMESTAMP> \
  --query "properties.error" -o json

# View Key Vault secrets
az keyvault secret list --vault-name averta-kv-staging -o table

# Test Container Apps connectivity
az containerapp logs show \
  -n averta-backend-staging \
  -g rg-averta-staging \
  --tail 100

# Verify private endpoints
az network private-endpoint list -g rg-averta-staging -o table
```

---

## 📁 Project Structure Reference

```
D:/Averta/
├── backend/                      # FastAPI + Prisma + Celery (LOCAL via Poetry)
│   ├── app/
│   │   ├── core/                 # Config, DB, Security, Middleware, Celery
│   │   ├── modules/              # 11 feature modules
│   │   ├── services/             # Shared services (storage, email, rules)
│   │   └── tasks/                # Celery tasks
│   ├── prisma/
│   │   ├── schema.prisma         # 25+ models
│   │   ├── migrations/           # 15+ migrations
│   │   └── seed.ts               # Seed data
│   ├── tests/                    # pytest (~78% coverage)
│   ├── Dockerfile                # Production only
│   ├── pyproject.toml            # Poetry deps + scripts
│   └── .env.example
├── frontend/                     # React 18 + Vite + Tailwind (LOCAL via pnpm)
│   ├── src/
│   │   ├── components/           # 50+ UI components
│   │   ├── pages/                # 30+ pages
│   │   ├── hooks/                # Custom hooks
│   │   ├── services/             # Axios + TanStack Query
│   │   └── contexts/             # AuthContext, etc.
│   ├── package.json
│   └── vite.config.ts
├── infra/
│   └── azure/                    # Azure Bicep Infrastructure
│       ├── bicep/
│       │   ├── main.bicep
│       │   ├── modules/          # 13 Bicep modules
│       │   └── environments/     # staging/ + production/
│       └── scripts/              # PowerShell deployment scripts
├── docker-compose.yml            # Infra only: postgres, redis, minio, mailhog
├── docker-compose.azure.yml      # Azure local dev: postgres, redis, azurite, mailhog
├── .env.example
└── QUICKSTART.md                 # This file
```

---

## 🔗 Quick Links

| Service | Local URL | Azure (Staging) |
|---------|-----------|-----------------|
| **Frontend** | http://localhost:3000 | https://staging.averta.com.br |
| **Backend API** | http://localhost:8000/docs | https://averta-backend-staging.azurecontainerapps.io/docs |
| **MinIO Console** | http://localhost:9001 | N/A (uses Azure Blob) |
| **Flower** | http://localhost:5555 | N/A |
| **Prisma Studio** | `poetry run prisma studio` | N/A |
| **Key Vault** | N/A | https://averta-kv-staging.vault.azure.net |
| **App Insights** | N/A | Azure Portal → Application Insights |

---

## 📞 Support

- **Backend Issues**: backend@averta.com.br
- **Frontend Issues**: frontend@averta.com.br
- **Infrastructure/DevOps**: platform@averta.com.br
- **Slack**: #averta-backend, #averta-frontend, #averta-platform
- **Confluence**: [Averta Architecture](https://averta.atlassian.net/wiki/spaces/BACK)

---

*Last updated: 2026-11-16 — Averta SaaS v1.0.0*