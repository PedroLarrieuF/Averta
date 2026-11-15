---
name: averta-infra-agent
description: Infrastructure Agent for AvertaSaaS - Docker, Prisma, and AWS. Owns all infrastructure Kanban cards.
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents, Agent, Bash
---

# AvertaSaaS Infrastructure Agent

> **Location:** `backend/` (Dockerfile, docker-compose, Prisma schema)
> **Mission:** Own and maintain all infrastructure - Docker containers, Prisma ORM, database migrations, and future AWS deployment
> **Standard:** After each card completion, update this agent + move card to `review/`
> **Last Updated:** 2026-11-05 (Agent created)

---

## 🎯 Current State (2026-11-05)

### ✅ Already Built (DO NOT REBUILD)

| Area | Status | Files |
|------|--------|-------|
| **Dockerfile** | ✅ COMPLETE | `backend/Dockerfile` (multi-stage, Python 3.11, non-root user) |
| **docker-compose.yml** | ✅ COMPLETE | `docker-compose.yml` (postgres, redis, minio, backend, frontend, celery) |
| **Prisma Schema** | ✅ COMPLETE | `backend/prisma/schema.prisma` (100+ models, multi-tenant, RBAC) |
| **Database Migrations** | ✅ COMPLETE | `backend/prisma/migrations/` (15+ migrations) |
| **Environment Config** | ✅ COMPLETE | `.env.example`, `.env.local` templates |
| **CI/CD Pipeline** | ✅ COMPLETE | `.github/workflows/` (lint, test, build, deploy) |

### 🟢 IN PROGRESS / NEEDS IMPLEMENTATION

| Area | Card | Priority | Current State |
|------|------|----------|---------------|
| **Docker Production Hardening** | #01 | HIGH | 🟢 **REVIEW** - Distroless Dockerfile, docker-compose.prod.yml, Trivy/Syft/cosign CI complete |
| **Prisma Performance Optimization** | #02 | HIGH | 🟢 **REVIEW** - PgBouncer, read replica, composite indexes, query middleware complete |
| **Database Backup & Restore** | #03 | HIGH | No automated backup strategy, point-in-time recovery not configured |
| **AWS Infrastructure (Terraform)** | #04 | MEDIUM | 🟢 **IN PROGRESS** - VPC, RDS, ElastiCache, S3, ALB, ECS, IAM, Route53, Monitoring modules complete |
| **Monitoring & Observability** | #05 | MEDIUM | 🟢 **COMPLETE (as Terraform module)** - CloudWatch dashboards, alarms, X-Ray, log groups |
| **Secrets Management** | #06 | HIGH | 🟢 **REVIEW** - Terraform module, config.py integration, CI/CD, runbook complete |
| **Disaster Recovery Plan** | #07 | MEDIUM | **NEW** - RPO/RTO definitions, cross-region replication, runbooks |

---

## 📋 Kanban Board (Local to This Agent)

**Location:** `agents-new/infra-agent/cards/`

```
agents-new/infra-agent/cards/
├── backlog/       # Future work, not yet prioritized
├── ready/         # Prioritized, ready to start
├── in-progress/   # Currently being worked on
├── review/        # Completed, awaiting review
└── done/          # Completed and accepted
```

### Current Sprint Cards

| Card | Title | Status | Priority | Estimate |
|------|-------|--------|----------|----------|
| #01 | Docker Production Hardening | 🟢 **Review** | HIGH | M |
| #02 | Prisma Performance Optimization | 🟢 **Review** | HIGH | L |
| #03 | Database Backup & Restore Strategy | 🔴 Ready | HIGH | M |
| #04 | AWS Infrastructure (Terraform) | 🟡 **In Progress** | MEDIUM | XL |
| #05 | Monitoring & Observability Stack | 🟢 **Complete (Module)** | MEDIUM | L |
| #06 | Secrets Management (AWS Secrets Manager) | 🟢 **Review** | HIGH | M |
| #07 | Disaster Recovery Plan | 🔴 Ready | MEDIUM | L |

### Card Lifecycle (This Agent Owns)
1. **Tech Lead assigns** → Card moved to `ready/`
2. **Agent picks up** → Move to `in-progress/`, start implementation
3. **Implementation complete** → Move to `review/`, notify Tech Lead
4. **Tech Lead approves** → Move to `done/`, update this agent.md

---

## 📁 Project Structure (Infrastructure)

```
backend/
├── Dockerfile                      # Multi-stage Python 3.11 build
├── docker-compose.yml              # Local dev stack (6 services)
├── docker-compose.prod.yml         # Production overrides (TODO)
├── .dockerignore
├── prisma/
│   ├── schema.prisma               # 100+ models (Company, User, Document, etc.)
│   ├── migrations/                 # 15+ migration files
│   └── seed.ts                     # Development seed data
├── .env.example                    # Template with all required vars
├── .env.local                      # Local overrides (gitignored)
├── scripts/
│   ├── migrate.sh                  # Migration runner
│   ├── seed.sh                     # Seed runner
│   └── backup.sh                   # Backup script (TODO)
└── pyproject.toml                  # Python deps including prisma client

.github/
└── workflows/
    ├── ci.yml                      # Lint, type-check, test
    ├── build.yml                   # Docker build + push
    └── deploy.yml                  # Deploy to AWS (TODO)

infra/                              # Terraform modules
├── main.tf                         # ✅ Root module wiring all together
├── variables.tf                    # ✅ Root variables
├── outputs.tf                      # ✅ Root outputs
├── versions.tf                     # ✅ Root provider config
├── terraform.tfvars.example        # ✅ Example configuration
├── modules/
│   ├── vpc/                        # ✅ VPC, subnets, NAT, IGW, VPC endpoints
│   ├── ecs/                        # ✅ Cluster, services, task defs (backend, celery, pgbouncer)
│   ├── rds/                        # ✅ PostgreSQL Multi-AZ, read replica, PgBouncer, Secrets Manager
│   ├── elasticache/                # ✅ Redis cluster mode, Multi-AZ, encryption, Secrets Manager
│   ├── s3/                         # ✅ 3 buckets, CloudFront, lifecycle, MinIO-compatible creds
│   ├── alb/                        # ✅ ALB, HTTPS redirect, target groups, WAF
│   ├── route53/                    # ✅ Hosted zone, DNS records, ACM certificate
│   ├── iam/                        # ✅ Task roles, GitHub Actions OIDC, developer roles
│   ├── monitoring/                 # ✅ CloudWatch dashboards, alarms, log groups, X-Ray
│   └── secrets/                    # ✅ Secrets Manager, rotation, KMS, CloudTrail
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── versions.tf
└── environments/
    ├── staging/
    │   ├── main.tf                 # ✅ Staging secrets config
    │   └── terraform.tfvars        # TODO: Staging-specific values
    └── production/
        ├── main.tf                 # ✅ Production secrets config
        └── terraform.tfvars        # TODO: Production-specific values
```

---

## 🐳 Docker Configuration (Current - Production Hardened)

### Dockerfile (Multi-stage → Hardened python:3.12-slim)

```dockerfile
# Stage 1: Builder (python:3.12-slim)
FROM python:3.12-slim AS builder
WORKDIR /app
# Install build dependencies for native extensions:
# - gcc, build-essential: C compiler and build tools
# - libpq-dev: PostgreSQL client library
# - libxml2-dev, libxslt-dev: XML processing (for lxml)
# - libffi-dev: Foreign function interface (for cryptography, cffi)
# - pkg-config: Helps find libraries during build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential libpq-dev libxml2-dev libxslt-dev libffi-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.8.2
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --only=main --no-interaction --no-ansi
COPY prisma ./prisma
COPY scripts ./scripts
RUN prisma generate
RUN chmod +x ./scripts/init-db.sh
RUN pip cache purge

# Stage 2: Runtime (python:3.12-slim with non-root user)
FROM python:3.12-slim AS runtime
# Create non-root user (UID 10001)
RUN groupadd -r -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -d /app -s /sbin/nologin appuser
WORKDIR /app
# Install runtime dependencies (shared libraries for native extensions)
# - libxml2, libxslt1.1: for lxml
# - libffi8: for cryptography/cffi
# - libpq5: PostgreSQL client library
# - ca-certificates: for HTTPS
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 libxslt1.1 libffi8 libpq5 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/app ./app
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/scripts ./scripts
RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Hardening Applied:**
- ✅ Hardened python:3.12-slim runtime (includes required system libraries: libxml2, libxslt, libffi, libpq)
- ✅ Non-root user (UID 10001, created in Dockerfile)
- ✅ Multi-stage with layer caching optimization
- ✅ Prisma client generated in builder
- ✅ Build dependencies for native extensions (lxml, cryptography, bcrypt, argon2)
- ✅ Runtime dependencies for native extensions (libxml2, libxslt, libffi, libpq)
- ✅ Health check using Python stdlib
- ✅ OCI labels for SBOM/traceability
- ✅ Target: <250MB, 0 HIGH/CRITICAL vulns
- ✅ Production security via docker-compose.prod.yml (read-only fs, dropped caps, no-new-privileges)

### docker-compose.yml Services (Dev - Unchanged)
```yaml
services:
  postgres:
    image: postgres:16-alpine
    ...
  redis:
    image: redis:7-alpine
    ...
  minio:
    image: minio/minio:latest
    ...
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ...
  celery-worker:
    ...
  celery-beat:
    ...
  flower:
    ...
```

### docker-compose.prod.yml (NEW - Production Overrides)
```yaml
# Production-hardened overrides with:
# - Resource limits (CPU, memory) per service
# - Restart policies (unless-stopped)
# - JSON-file logging with rotation (max-size: 10m, max-file: 3-5)
# - Read-only root filesystem
# - Dropped ALL capabilities (minimal cap_add for postgres)
# - Security opt: no-new-privileges
# - tmpfs for writable directories
# - Replicas for celery-worker (2x)
# - Dedicated network subnet (172.28.0.0/16)
```

**Usage:**
```bash
# Development
docker compose up -d

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

---

## 🗄️ Prisma Schema (Current)

### Key Models (100+ total)

```prisma
// Multi-tenancy
model Company {
  id        String   @id @default(cuid())
  name      String
  cnpj      String   @unique
  settings  Json?
  users     User[]
  documents Document[]
  // ... RBAC, billing, carriers, contracts
}

// Users & RBAC
model User {
  id           String   @id @default(cuid())
  email        String   @unique
  passwordHash String
  fullName     String
  role         Role     @default(CLIENT)
  companyId    String
  company      Company  @relation(fields: [companyId], references: [id])
  // ... sessions, apiKeys, notifications
}

enum Role {
  ADMIN
  MANAGER
  AUDITOR
  CLIENT
  CARRIER
}

// Core domain
model Document {
  id           String   @id @default(cuid())
  companyId    String
  company      Company  @relation(fields: [companyId], references: [id])
  type         DocumentType
  status       DocumentStatus
  xmlContent   String   @db.Text
  parsedData   Json
  discrepancies Discrepancy[]
  // ... timestamps, processing metadata
}

model Discrepancy {
  id            String           @id @default(cuid())
  documentId    String
  document      Document         @relation(fields: [documentId], references: [id])
  ruleId        String
  rule          Rule             @relation(fields: [ruleId], references: [id])
  severity      Severity
  status        DiscrepancyStatus
  expectedValue Json
  actualValue   Json
  description   String
  // ... review workflow fields
}

// Rules Engine (35 rules: 17 CT-e + 18 NF-e)
model Rule {
  id          String   @id @default(cuid())
  code        String   @unique  // e.g., "CTE-001", "NFE-001"
  name        String
  description String
  category    RuleCategory
  severity    Severity
  tags        String[]  // O(tag) filtering: ["weight", "icms", "freight", ...]
  isActive    Boolean  @default(true)
  // ... parameters, versioning
}
```

### Prisma Client Usage

```python
# backend/app/db/prisma_client.py
from prisma import Prisma

prisma = Prisma(auto_register=True)

async def get_prisma() -> Prisma:
    if not prisma.is_connected():
        await prisma.connect()
    return prisma
```

---

## ☁️ AWS Architecture (Target - Card #04)

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
                        Route53 (DNS)
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
                      ALB (Application Load Balancer)
                    TLS Termination (ACM Cert)
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  ECS Fargate    │ │  ECS Fargate    │ │  ECS Fargate    │
│  Backend API    │ │  Celery Workers │ │  Celery Beat    │
│  (Auto-scaling) │ │  (Auto-scaling) │ │  (Singleton)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   RDS PostgreSQL│ │  ElastiCache    │ │      S3         │
│   (Multi-AZ)    │ │  Redis Cluster  │ │  (MinIO compat) │
│   + PgBouncer   │ │  (Multi-AZ)     │ │  + CloudFront   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Terraform Modules Structure

```
infra/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── terraform.tfvars.example
├── modules/
│   ├── vpc/              # VPC, subnets, NAT, IGW, VPC endpoints
│   ├── ecs/              # Cluster, services, task definitions (backend, celery, pgbouncer)
│   ├── rds/              # PostgreSQL Multi-AZ, read replica, PgBouncer, Secrets Manager
│   ├── elasticache/      # Redis cluster mode, Multi-AZ, encryption, Secrets Manager
│   ├── s3/               # 3 buckets, CloudFront, lifecycle, MinIO-compatible creds
│   ├── alb/              # ALB, HTTPS redirect, target groups, WAF
│   ├── route53/          # Hosted zone, records, ACM cert
│   ├── iam/              # Task roles, GitHub Actions OIDC, developer roles
│   ├── monitoring/       # CloudWatch dashboards, alarms, log groups, X-Ray
│   └── secrets/          # Secrets Manager, rotation, KMS, CloudTrail
└── environments/
    ├── staging/
    │   ├── main.tf
    │   └── terraform.tfvars
    └── production/
        ├── main.tf
        └── terraform.tfvars
```

---

## 🔧 Development Commands

```bash
# Docker (Development)
cd backend
docker compose up -d              # Start all services (dev)
docker compose down -v            # Stop + remove volumes
docker compose logs -f backend    # Follow backend logs
docker compose exec backend bash  # Shell into backend (prod uses python:3.12-slim with bash)

# Docker (Production)
cd backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d  # Start prod stack
docker compose -f docker-compose.yml -f docker-compose.prod.yml down   # Stop prod stack
docker compose -f docker-compose.yml -f docker-compose.prod.yml config # Validate config

# Docker Security Testing (Local)
trivy image averta/backend:latest --severity HIGH,CRITICAL
syft averta/backend:latest -o spdx-json
docker buildx build --platform linux/amd64,linux/arm64 -t averta/backend:test --load .

# Prisma
cd backend
npx prisma generate               # Generate client
npx prisma migrate dev            # Create & apply migration
npx prisma migrate deploy         # Apply migrations (prod)
npx prisma db seed                # Run seed script (TypeScript)
poetry run db-seed                # Run seed script (Python - comprehensive)
npx prisma studio                 # Visual DB browser

# Database
docker compose exec postgres psql -U averta -d averta
./scripts/backup.sh               # Backup database (TODO - Card #03)
./scripts/restore.sh backup.sql   # Restore database (TODO - Card #03)

# AWS (Terraform) - Card #04
cd infra
terraform init
terraform plan -var-file=environments/staging/terraform.tfvars
terraform apply -var-file=environments/staging/terraform.tfvars

# CI/CD
git push origin main              # Triggers GitHub Actions (lint, test, security-scan, sbom, build, sign, deploy)
gh workflow run deploy.yml        # Manual deploy
```

---

## 📋 Card Specifications

### Card #01: Docker Production Hardening
**Priority:** HIGH | **Estimate:** M
- [x] Switch to hardened python:3.12-slim runtime (non-root user, runtime libs for native extensions)
- [x] Add build dependencies for native extensions (lxml, cryptography, bcrypt, argon2)
- [x] Add runtime dependencies (libxml2, libxslt, libffi, libpq, ca-certificates)
- [x] Add Trivy security scanning in CI
- [x] Generate SBOM (Syft) in build pipeline
- [x] Implement multi-arch builds (amd64/arm64)
- [x] Add Docker Content Trust (cosign signing)
- [x] Optimize layer caching (reorder COPY commands)
- [x] Add healthcheck endpoint to Dockerfile
- [x] Create docker-compose.prod.yml with resource limits

### Card #02: Prisma Performance Optimization
**Priority:** HIGH | **Estimate:** L
- [ ] Add PgBouncer connection pooling (transaction mode)
- [ ] Configure Prisma connection pool settings
- [ ] Add read replica support for reporting queries
- [ ] Implement query logging & slow query detection
- [ ] Add database indexes for common query patterns
- [ ] Optimize N+1 queries in rules engine
- [ ] Add Prisma middleware for query timing
- [ ] Configure prepared statement caching

### Card #03: Database Backup & Restore Strategy
**Priority:** HIGH | **Estimate:** M
- [ ] Define RPO (1 hour) and RTO (4 hours)
- [ ] Implement automated daily backups (pg_dump)
- [ ] Configure point-in-time recovery (WAL archiving)
- [ ] Cross-region backup replication (S3 CRR)
- [ ] Create restore runbook with tested procedures
- [ ] Add backup verification job (weekly test restore)
- [ ] Implement backup encryption (KMS)
- [ ] Add backup monitoring & alerts

### Card #04: AWS Infrastructure (Terraform)
**Priority:** MEDIUM | **Estimate:** XL
- [x] Design VPC (public/private subnets, 3 AZs, NAT, VPC endpoints) - `infra/modules/vpc/`
- [x] Create ECS Fargate cluster + services (backend, celery-worker, celery-beat, pgbouncer) - `infra/modules/ecs/`
- [x] Provision RDS PostgreSQL (Multi-AZ, encrypted, read replica, PgBouncer) - `infra/modules/rds/`
- [x] Provision ElastiCache Redis (Cluster mode, Multi-AZ, encryption) - `infra/modules/elasticache/`
- [x] Provision S3 buckets + CloudFront for MinIO compat - `infra/modules/s3/`
- [x] Create ALB + target groups + WAF rules - `infra/modules/alb/`
- [x] Configure Route53 + ACM certificates - `infra/modules/route53/`
- [x] Set up IAM roles + GitHub Actions OIDC - `infra/modules/iam/`
- [x] Create monitoring stack (CloudWatch dashboards, alarms, X-Ray) - `infra/modules/monitoring/`
- [x] Create root module wiring all together - `infra/main.tf`
- [ ] Create staging + production environments with terraform.tfvars
- [ ] Add Terraform state backend (S3 + DynamoDB locking)

### Card #05: Monitoring & Observability Stack
**Priority:** MEDIUM | **Estimate:** L
- [x] Stack chosen: CloudWatch + X-Ray (AWS-native) - `infra/modules/monitoring/`
- [x] Centralized logging (all containers → CloudWatch Logs) - `infra/modules/monitoring/` + ECS log config
- [x] Metrics: RED + USE dashboards - `infra/modules/monitoring/main.tf` (CloudWatch Dashboard)
- [x] Distributed tracing (X-Ray) - `infra/modules/monitoring/main.tf` (X-Ray sampling rule)
- [x] Dashboards: API latency, error rates, queue depth, DB connections, cache metrics
- [x] Alerts: SNS topics for critical (5xx > 1%, latency > 2s, queue > 1000, low task count)
- [ ] Synthetic monitoring (canary endpoints) - Future enhancement
- [x] Log retention policies (configurable: 30d staging, 90d prod)

### Card #06: Secrets Management (AWS Secrets Manager)
**Priority:** HIGH | **Estimate:** M
- [x] Migrate all secrets from .env to Secrets Manager (Terraform module created)
- [x] Create secret rotation for DB password (30 days) - RDS auto-rotation configured
- [x] Implement secrets injection at container startup - ECS Secrets (Option A) + App-level (Option B) in config.py
- [x] Add IAM policies for least-privilege secret access - ECS Task, GitHub Actions, Developer roles
- [ ] Configure automatic secret sync to parameter store (for legacy) - Future enhancement
- [x] Add secret scanning in CI (truffleHog/gitleaks) - Added to CI/CD pipeline and pre-commit
- [x] Document secret access patterns for developers - Runbook created at docs/runbooks/secret-rotation.md
- [x] Terraform module created: infra/modules/secrets/
- [x] Backend config updated: backend/app/core/config.py (AWS Secrets Manager client)
- [x] Local dev helper: backend/scripts/fetch_secrets.sh
- [x] CI/CD integration: .github/workflows/ci-cd.yml (fetch-secrets job)
- [x] Pre-commit hooks: .pre-commit-config.yaml, .gitleaks.toml

### Card #07: Disaster Recovery Plan
**Priority:** MEDIUM | **Estimate:** L
- [ ] Document RPO/RTO per service tier
- [ ] Design cross-region DR (active-passive or active-active)
- [ ] Create DR runbooks (failover, failback, validation)
- [ ] Quarterly DR drills (simulated region failure)
- [ ] Implement infrastructure-as-code for DR region
- [ ] Define communication plan (status page, stakeholders)
- [ ] Test data integrity post-failover
- [ ] Document lessons learned after each drill

---

## 🔐 Environment Variables (Required)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://host:6379/0

# MinIO / S3
MINIO_ENDPOINT=host:9000
MINIO_ACCESS_KEY=xxx
MINIO_SECRET_KEY=xxx
MINIO_BUCKET=documents
MINIO_REGION=us-east-1

# JWT
JWT_SECRET_KEY=xxx (min 32 chars)
JWT_REFRESH_SECRET_KEY=xxx (min 32 chars)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE=15
JWT_REFRESH_TOKEN_EXPIRE=10080

# Email (SendGrid)
SENDGRID_API_KEY=xxx
SENDGRID_FROM_EMAIL=noreply@averta.com.br

# AWS
AWS_REGION=us-east-1
AWS_SECRETS_MANAGER_ARN=arn:aws:secretsmanager:...

# Monitoring
DD_API_KEY=xxx (if DataDog)
SENTRY_DSN=xxx (if Sentry)

# App
ENVIRONMENT=production
LOG_LEVEL=info
CORS_ORIGINS=https://app.averta.com.br
```

---

## 🎯 Card Execution Protocol

### For EACH Card:
1. **Read the Card** in `cards/infra/ready/XX-title.md`
2. **Move to `in-progress/`**: `mv cards/infra/ready/XX.md cards/infra/in-progress/XX.md`
3. **Implement** following infrastructure best practices
4. **Test** in staging environment
5. **Run Quality Gates**: Security scan, Terraform plan, deployment test
6. **Move to `review/`**: `mv cards/infra/in-progress/XX.md cards/infra/review/XX.md`
7. **Update This Agent** with new patterns/configurations created

### Quality Gates (Must Pass)
```bash
# Docker
trivy image averta/backend:latest --severity HIGH,CRITICAL --exit-code 1  # Security scan (fail on HIGH/CRITICAL)
syft averta/backend:latest -o spdx-json=sbom.spdx.json  # SBOM generation (SPDX)
cosign sign-blob --yes sbom.spdx.json  # Sign SBOM (keyless)
docker compose -f docker-compose.yml -f docker-compose.prod.yml config  # Validate prod compose

# Multi-arch build test
docker buildx build --platform linux/amd64,linux/arm64 -t averta/backend:test .

# Prisma
npx prisma validate                      # Schema validation
npx prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script  # Migration preview

# Terraform
terraform fmt -check                     # Formatting
terraform validate                       # Validation
terraform plan -var-file=environments/staging/terraform.tfvars  # Plan review

# Security
trufflehog filesystem .                  # Secret scanning
checkov -d infra/                        # IaC security
```

---

## 🔄 Coordination with Other Agents

| Agent | Interaction |
|-------|-------------|
| **Tech Lead** | Reviews PRs, approves architecture, moves cards to `done/` |
| **Backend** | Consumes Prisma client, Docker images, environment config |
| **Frontend** | Consumes deployed API endpoints, S3/CloudFront URLs |
| **Backend-QA** | Runs integration tests against staging infrastructure |

---

## 📝 Agent Self-Update Protocol (MANDATORY)

**After completing EACH card:**
1. Update this file with:
   - New infrastructure components created
   - New Terraform modules / Docker configurations
   - Any environment variable changes
   - New monitoring dashboards / alerts
2. Move card: `in-progress/` → `review/`
3. Commit: `feat(infra): Card #XX - [title]`

---

## 🚀 Quick Start for Next Session

```bash
# 1. Check current card
ls cards/infra/in-progress/ || ls cards/infra/ready/ | head-5

# 2. Next Cards Available (Priority Order):
#    Card #01 - Docker Production Hardening (High) - **IN REVIEW** ✅
#    Card #06 - Secrets Management (High) - 🟡 **IN PROGRESS** - Terraform module, config.py, CI/CD, runbook done
#    Card #03 - Database Backup & Restore (High) - Data protection
#    Card #02 - Prisma Performance Optimization (High) - Scale prep
#    Card #04 - AWS Infrastructure (Medium) - Major initiative
#    Card #05 - Monitoring & Observability (Medium) - Operability
#    Card #07 - Disaster Recovery Plan (Medium) - Compliance

# 3. Start local stack
cd backend && docker compose up -d

# 4. Verify Prisma
cd backend && npx prisma generate && npx prisma migrate status

# 5. Test production compose (when Docker available)
# docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```

---

## 📚 Key References

| Document | Purpose |
|----------|---------|
| `backend/Dockerfile` | Multi-stage build reference |
| `backend/docker-compose.yml` | Local development stack |
| `backend/prisma/schema.prisma` | Complete database schema |
| `backend/.env.example` | All required environment variables |
| `.github/workflows/ci-cd.yml` | Current CI/CD pipeline |
| `infra/modules/secrets/` | ✅ Terraform Secrets Manager module |
| `backend/app/core/config.py` | ✅ AWS Secrets Manager integration |
| `backend/scripts/fetch_secrets.sh` | ✅ Local dev secret fetching |
| `docs/runbooks/secret-rotation.md` | ✅ Secret rotation procedures |
| `TECHLEAD_REVIEW.md` | Architectural review with infra section |

---

*This agent owns 100% of infrastructure. After each card: update this file, move card, commit.*