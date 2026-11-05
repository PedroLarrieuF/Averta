---
name: averta-backend-agent
description: Specialized agent for AvertaSaaS backend development (Python FastAPI + Prisma + Celery + PostgreSQL + Redis)
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Backend Agent (Python FastAPI) - v2.2

## Project Context

**Location:** `backend/`
**Tech Stack:** FastAPI 0.109 (async) + Prisma Client Python + PostgreSQL 16 + Redis 7 + Celery 5 + MinIO/S3 + SendGrid

## Architecture Overview

```
backend/
├── app/
│   ├── core/                    # Config, DB, Security, Middleware, Celery
│   │   ├── config.py            # Pydantic Settings (.env)
│   │   ├── database.py          # Prisma singleton + lifespan
│   │   ├── security.py          # JWT, bcrypt, password hash
│   │   ├── exceptions.py        # Exception hierarchy (AppException → NotFoundError, ValidationError, ForbiddenError)
│   │   ├── dependencies.py      # FastAPI Depends (auth, pagination, company, client context)
│   │   ├── middleware.py        # RequestID, Logging, SecurityHeaders
│   │   └── celery_app.py        # Celery config + beat schedule
│   ├── modules/                 # 11 Feature modules (Clean Architecture)
│   │   ├── auth/                # Login, register, me, refresh, password reset
│   │   ├── users/               # CRUD usuários, roles, status
│   │   ├── companies/           # CRUD empresas, settings
│   │   ├── clients/             # CRUD clientes, branches
│   │   ├── carriers/            # CRUD transportadoras
│   │   ├── branches/            # CRUD filiais
│   │   ├── contracts/           # Contratos + FreightTables (versionamento)
│   │   ├── documents/           # Upload, parse, reprocess, list
│   │   ├── discrepancies/       # List, summary, bulk status, review
│   │   ├── contests/            # Workflow completo + PDF + payments
│   │   ├── reports/             # Dashboard, PDF, Excel, scheduled
│   │   └── notifications/       # In-app + Email + Preferences
│   ├── services/                # Shared business logic
│   │   ├── xml_parser.py        # CT-e/NF-e namespace-aware parser (40+ campos)
│   │   ├── rules_engine_v2.py   # Engine v2 + factory + tag-based filtering
│   │   ├── rules_critical.py    # 17 rules implementation
│   │   ├── pdf_generator.py     # ReportLab contest letter
│   │   ├── storage.py           # MinIO/S3 CRUD + presigned URLs
│   │   └── email_service.py     # SendGrid + 7 Jinja2 templates
│   ├── tasks/                   # Celery tasks
│   │   ├── documents.py         # process_document, reprocess
│   │   └── discrepancies.py     # bulk_recalc, notifications
│   ├── templates/emails/        # 7 templates (HTML + .txt)
│   │   ├── discrepancy_alert
│   │   ├── contest_created
│   │   ├── weekly_report
│   │   ├── contract_expiring
│   │   ├── payment_received
│   │   ├── welcome
│   │   └── password_reset
│   └── data/                    # Static reference data
│       ├── icms_rules.json      # 27 UFs, alíquotas, FCP, ST por NCM/UF
│       └── sicoban_table.json   # 22 faixas CEP×tipo×modal, pisos ANTT
├── tests/
│   ├── conftest.py
│   └── test_rules_critical.py   # 50+ testes pytest-asyncio
├── prisma/schema.prisma         # 25 models + enums
├── Dockerfile                   # Multi-stage (builder + runtime)
├── docker-compose.yml           # Postgres, Redis, MinIO, Backend, Celery, Flower
├── .github/workflows/ci-cd.yml  # Lint, test, build, deploy
├── pyproject.toml               # Poetry deps + scripts
├── .env.example                 # Template variáveis
└── README.md                    # Comprehensive documentation
```

## Core Concepts

### Kanban Board (Local to This Agent)

**Location:** `agents-new/backend-agent/cards/`

```
agents-new/backend-agent/cards/
├── backlog/       # Future work, not yet prioritized
├── ready/         # Prioritized, ready to start
├── in-progress/   # Currently being worked on
├── review/        # Completed, awaiting review
└── done/          # Completed and accepted
```

### Current Sprint Cards (2026-11-04)

| Card | Title | Status | Priority | Estimate |
|------|-------|--------|----------|----------|
| #04 | Rate Limiter Redis (slowapi) | ✅ **Done** | HIGH | M |
| #05 | Rules Engine Redis Cache | ✅ **Done** | HIGH | M |
| #12 | XML Parser Namespace Fix (NF-e 4.00) | ✅ **Done** | HIGH | M |
| #13 | Integration Tests (httpx.AsyncClient) | 🟡 In Progress | MEDIUM | L |
| #14 | PDF Generator Threadpool | 🟡 In Progress | MEDIUM | M |
| #16 | Rules DB-Driven Configuration | 🔴 Ready | MEDIUM | L |
| #28 | Fix Failing Rule Tests | ✅ **Done** | HIGH | M |
| #29 | Backend Integration Tests (httpx.AsyncClient) | 🔴 Ready | HIGH | L |
| #30 | Fix Rate Limit Module Test Import | ✅ **Done** | HIGH | S |
| #33 | Fix Linting Issues (ruff) | 🔴 Ready | MEDIUM | M |
| #34 | NF-e Critical Rules (5 rules) | ✅ **Done** | CRITICAL | L |
| #35 | NF-e High Priority Rules (7 rules) | ✅ **Done** | HIGH | L |
| #36 | NF-e Medium Priority Rules (6 rules) | ✅ **Done** | MEDIUM | M |

### Backlog Cards

| Card | Title | Priority | Estimate |
|------|-------|----------|----------|
| #17 | ML Anomaly Detection | MEDIUM | XL |
| #18 | Webhooks System | MEDIUM | L |
| #19 | Audit Log Middleware | HIGH | M |
| #20 | Soft Delete Global | MEDIUM | M |

### Card Lifecycle (This Agent Owns)
1. **Tech Lead assigns** → Card moved to `ready/`
2. **Agent picks up** → Move to `in-progress/`, start implementation
3. **Implementation complete** → Move to `review/`, notify Tech Lead
4. **Tech Lead approves** → Move to `done/`, update this agent.md

---

### Multi-tenancy
- All models scoped by `company_id` (injected via middleware)
- Role `CLIENT` gets additional `client_id` scoping
- RBAC: ADMIN > MANAGER > AUDITOR > CLIENT > CARRIER

### Document Processing Pipeline
```
POST /documents/upload (XML CT-e/NF-e)
    → CREATE Document (status=PENDING)
    → Celery task: process_document(doc_id)
        → xml_parser.parse(xml) → 40+ fields extracted
        → Auto-match contract (carrier + client + vigência)
        → RulesEngineV2.evaluate_all(RuleContext)
        → CREATE Discrepancy[] (status=OPEN)
        → UPDATE Document (status=COMPLETED)
        → notify_discrepancy_found() → email
```

### Rules Engine v2 (35 Rules)

**CT-e Rules (17):**
| Code | Name | Type | Severity | Tags |
|------|------|------|----------|------|
| ICMS_DIFAL | ICMS Diferencial (DIFAL) | ICMS_DIFFERENTIAL | HIGH | icms, interstate |
| ICMS_FCP | FCP - Fundo Combate Pobreza | ICMS_FCP | HIGH | icms, interstate |
| ICMS_ST | ICMS Substituição Tributária | ICMS_ST | HIGH | icms, icms_st |
| FRETE_PESO_VALOR | Frete Peso × Valor (faixas) | FREIGHT_WEIGHT_VALUE | HIGH | freight, weight |
| FRETE_CUBAGE | Frete Cubagem (m³) | FREIGHT_CUBAGE | HIGH | freight, cubage |
| PESO_REAL_VS_FATURADO | Peso Real vs Faturado | PESO_REAL_VS_FATURADO | HIGH | weight |
| VALOR_MINIMO_FRETE | Piso Mínimo ANTT 5.839/2021 | VALOR_MINIMO_FRETE | CRITICAL | freight, weight |
| REDESPACHO_VALIDACAO | Redespacho (CT-e comp.) | REDESPACHO | HIGH | redespacho |
| PEDAGIO_CONFERENCIA | Conferência Pedágio | TOLL_PLAZA | MEDIUM | toll |
| AD_VALOREM | Ad Valorem (seguro valor) | AD_VALOREM | MEDIUM | advalorem |
| GRIS | Gerenciamento Risco | GRIS | MEDIUM | gris |
| SICOBAN_TABLE_REAL | Tabela Sicoban/ANTT (CEP) | SICOBAN_TABLE | HIGH | freight, sicoban |
| CTE_ANULACAO | CT-e Anulação (tpEmis=3) | COMPLEMENTARY_CTE | HIGH | cte_complementar |
| CTE_SUBSTITUICAO | CT-e Substituição (tpEmis=2) | COMPLEMENTARY_CTE | HIGH | cte_complementar |
| CTE_COMPLEMENTO_VALOR | CT-e Complemento (tpEmis=4) | COMPLEMENTARY_CTE | MEDIUM | cte_complementar |
| COMPLEMENTARY_CTE | (Genérico) | COMPLEMENTARY_CTE | MEDIUM | cte_complementar |
| ML_ANOMALY | ML Anomaly Detection | OTHER | MEDIUM | ml, anomaly |

**NF-e Rules (18 implemented):**
| Code | Name | Type | Severity | Tags |
|------|------|------|----------|------|
| NFE_ICMS_CALCULO | Validação Cálculo ICMS NF-e | ICMS_CALCULO | CRITICAL | nfe, icms |
| NFE_ICMS_ST | Validação ICMS ST NF-e | ICMS_ST | CRITICAL | nfe, icms_st |
| NFE_DIFAL | Validação DIFAL NF-e | DIFAL | CRITICAL | nfe, interstate |
| NFE_FRETE_NA_BASE | Frete na Base ICMS NF-e | FRETE_BASE | CRITICAL | nfe, freight |
| NFE_CTE_CROSS | Cross-validation NF-e/CT-e | CTE_CROSS | CRITICAL | nfe, cte |
| NFE_FCP | Validação FCP NF-e | ICMS_FCP | HIGH | nfe, fcp, interstate |
| NFE_CFOP_FRETE | Validação CFOP Frete NF-e | CFOP_VALIDATION | HIGH | nfe, cfop, freight |
| NFE_CFOP_INTERSTADUAL | Validação CFOP Interestadual NF-e | CFOP_VALIDATION | HIGH | nfe, cfop, interstate |
| NFE_NCM_CEST | Validação NCM/CEST NF-e | NCM_CEST | HIGH | nfe, ncm, cest |
| NFE_VALOR_TOTAL | Validação Valor Total NF-e | VALOR_TOTAL | HIGH | nfe, total |
| NFE_TRANSPORTADORA | Validação Transportadora NF-e | TRANSPORTADORA | HIGH | nfe, carrier |
| NFE_DESTINATARIO | Validação Destinatário NF-e | DESTINATARIO | HIGH | nfe, recipient |
| NFE_PESO_VOLUME | Validação Peso/Volume NF-e | PESO_VOLUME | MEDIUM | nfe, weight, volume |
| NFE_COMPLEMENTAR | Validação NF-e Complementar | COMPLEMENTAR | MEDIUM | nfe, complementary |
| NFE_CARTA_CORRECAO | Validação Carta Correção NF-e | CARTA_CORRECAO | MEDIUM | nfe, correction |
| NFE_CANCELAMENTO | Validação Cancelamento NF-e | CANCELAMENTO | MEDIUM | nfe, cancellation |
| NFE_INUTILIZACAO | Validação Inutilização NF-e | INUTILIZACAO | MEDIUM | nfe, inutilization |
| NFE_REGIME_ESPECIAL | Validação Regime Especial NF-e | REGIME_ESPECIAL | MEDIUM | nfe, regime |

**Smart Filtering:** `engine.get_relevant_rules(context)` uses `relevance_tags` for O(tag) vs O(total) performance

### Success-Fee Model
```
success_fee = total_recovered * (contract.success_fee_pct / 100)
net_recovery = total_recovered - success_fee
```

## Development Commands

```bash
cd backend

# Docker Compose (recommended)
cp .env.example .env   # Edit secrets
docker-compose up -d --build
docker-compose exec backend poetry run prisma db push
docker-compose exec backend poetry run prisma generate

# Local (Poetry)
poetry install --with dev
poetry run prisma generate
poetry run prisma db push
poetry run start          # uvicorn app.main:app --reload (port 8000)
poetry run worker         # celery worker
poetry run beat           # celery beat
poetry run flower         # Flower monitoring (port 5555)

# Testing
poetry run test-cov       # All with coverage
poetry run pytest tests/test_rules_critical.py -v  # Rules only
poetry run pytest -m "unit" -v
poetry run pytest -m "integration" -v
```

## Environment Variables (.env)

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=<32+ chars, openssl rand -base64 32>
JWT_REFRESH_SECRET_KEY=<32+ chars>
SENDGRID_API_KEY=SG.xxx          # or SMTP_*
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
FRONTEND_URL=http://localhost:3000
SUCCESS_FEE_PERCENTAGE=20.0
```

## Key API Endpoints

- **Swagger:** `http://localhost:8000/docs`
- **Health:** `GET /health`
- **OpenAPI:** `GET /api/v1/openapi.json`

### Auth (`/api/v1/auth`)
- `POST /login` - Access (15min) + Refresh (7d) tokens
- `POST /register` - Company + User creation
- `POST /refresh` - Token refresh
- `POST /logout` - Revoke refresh token
- `GET /me` - Current user
- `POST /forgot-password` / `POST /reset-password`

### Documents (`/api/v1/documents`)
- `POST /upload` - Multipart XML upload
- `POST /import` - Base64 XML import
- `GET /` - List with filters/pagination
- `GET /{id}` - Document details + parsed data
- `POST /{id}/reprocess` - Re-run rules engine

### Discrepancies (`/api/v1/discrepancies`)
- `GET /` - List with filters (status, severity, rule, date)
- `GET /summary` - KPIs by status/severity/rule
- `PATCH /bulk-status` - Bulk status update
- `POST /{id}/review` - Mark as reviewed

### Contests (`/api/v1/contests`)
- `POST /` - Create from selected discrepancies
- `GET /` - List with workflow status
- `GET /{id}` - Contest details + items + communications
- `POST /{id}/send` - Generate PDF + send to carrier
- `PATCH /{id}/negotiate` - Update status (ACKNOWLEDGED, NEGOTIATING, ACCEPTED, PARTIAL, REJECTED)
- `POST /{id}/payments` - Register payment → triggers fee calc + notifications

### Reports (`/api/v1/reports`)
- `GET /dashboard` - KPIs, top carriers, top rules, time series
- `GET /pdf` - ReportLab PDF export
- `GET /excel` - OpenPyXL multi-sheet export
- `POST /schedule` - Configure weekly email report

## Database Schema (Prisma - 25 Models)

Key models: `Company`, `User`, `Client`, `ClientBranch`, `Carrier`, `Branch`, `Contract`, `FreightTable`, `Document`, `Discrepancy`, `Contest`, `ContestItem`, `Communication`, `Payment`, `Notification`, `NotificationPreferences`, `AuditLog`

Enums: `UserRole`, `UserStatus`, `DocumentStatus`, `DocumentType`, `DiscrepancyStatus`, `DiscrepancySeverity`, `ContestStatus`, `ContestItemStatus`, `CommunicationType`, `NotificationType`, `NotificationChannel`

## Testing Strategy

- **Unit tests:** Rules engine (50+ tests in `test_rules_critical.py`)
- **Coverage:** ~78% (rules, services, parsers)
- **Markers:** `unit`, `integration`, `slow`

### Critical Test Cases
- `test_icms_diferential_triggered` / `not_triggered` / `same_uf`
- `test_fcp_rule` (BA=2%, SP=0%)
- `test_icms_st_rule` (NCM 22030000, CST 10, SP=18%)
- `test_freight_weight_value` / `cubage` (faixas + mínimos)
- `test_peso_real_vs_faturado` (tolerância 5% / 20%)
- `test_valor_minimo_frete` (3 eixos × 500km × 1.2 = 1470)
- `test_cte_anulacao_without_ref` (CRITICAL)
- `test_engine_creation` (17 rules registradas)
- `test_engine_filtering` (tag-based relevance)
- `test_full_audit` (documento com 5+ divergências)

### ⚠️ CURRENT TEST FAILURES (2026-11-03)

The following tests are FAILING and need to be fixed (Card #28):

| Test | File | Issue |
|------|------|-------|
| `test_peso_real_vs_faturado` | `test_rules_critical.py` | Rule logic / tolerance calculation |
| `test_valor_minimo_frete` | `test_rules_critical.py` | ANTT table lookup / calculation |
| `test_cte_anulacao_without_ref` | `test_rules_critical.py` | CT-e complementar logic |
| `test_engine_cache_consistency` | `test_rules_critical.py` | Redis cache key generation |
| `test_rules_engine_integration` | `test_rules_critical.py` | Full audit flow |
| `test_rate_limit_import` | `tests/...` | `app.core.rate_limit` module import error |

**Action Required:** Fix these 6 failing tests before proceeding with new features.

## CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

1. **lint-and-test** - ruff, mypy, pytest + coverage → Codecov
2. **build-and-push** (main) - Docker Buildx → GHCR
3. **deploy-staging** (develop) - kubectl/Helm staging
4. **deploy-production** (main, manual) - Blue/green production

## Known Technical Debt (Updated 2026-11-04)

| ID | Area | Description | Status |
|----|------|-------------|--------|
| TD-001 | xml_parser.py | NF-e 4.00 namespace frágil; migrar para lxml.etree | ✅ **DONE** (Card #12) |
| TD-002 | rules_engine_v2.py | Cache Redis stub (`_cache = None`) | ✅ **DONE** (Card #05) |
| TD-003 | pdf_generator.py | Bloqueia event loop; usar `run_in_threadpool` | 🟡 In Progress (Card #14, #41) |
| TD-004 | Rate Limiting | In-memory não funciona em múltiplas réplicas | ✅ **DONE** (Card #04) |
| TD-005 | Integration Tests | Faltam `httpx.AsyncClient` tests | 🟡 In Progress (Card #13, #29, #37) |
| TD-009 | Rules Tests | 6 tests failing (PesoReal, ValorMinimo, CTE_Anulacao, Cache, Integration) | ✅ **DONE** (Card #28) |
| TD-010 | Rate Limit Module | `app.core.rate_limit` import failing in tests | ✅ **DONE** (Card #30) |
| TD-011 | Linting | 200+ ruff issues (import sorting, print statements, unused imports) | 🔴 Open (Card #33) |
| TD-012 | NF-e Rules | 18 NF-e rules missing implementations (0/18) | ✅ **DONE** (Cards #34, #35, #36 - all 18 implemented) |

## Future Roadmap (from README)

### Short Term (1-2 sprints)
- Rate Limiting Redis (slowapi + sliding window) ✅ DONE
- Webhooks para ERP/TMS externo (Card #18)
- Audit Log completo (middleware automático) (Card #19)
- Soft Delete Global (deleted_at + BaseService filter) (Card #20)
- OpenAPI Examples

### Medium Term (1-2 months)
- Rules DB-Driven (CRUD no painel + JSON logic + versionamento) (Card #16)
- ML Anomaly Detection (Isolation Forest sobre difference_pct histórico) (Card #17)
- Multi-modal Freight (aéreo, marítimo, ferroviário)
- EDI/Integração TMS (parser layout Carga/Descarga)
- Advanced Scheduling (Celery Beat dynamic via admin UI)

### Long Term (3-6 months)
- Multi-region Deploy (latency-based, LGPD data residency)
- GraphQL Gateway (Apollo/Strawberry federation)
- Event Sourcing (Kafka audit trail imutável + replay)
- AI-assisted Contest (LLM para argumentação jurídica)
- White-label (tenant branding)

## Agent Instructions

When working on the backend:

1. **Follow Clean Architecture** - core → modules → services → tasks
2. **Use BaseService Pattern** - CRUD padronizado, paginação, filtros, soft-delete opcional
3. **Dependency Injection** - FastAPI `Depends` para DB, auth, pagination, company/client context
4. **Structured Logging** - `structlog` JSON em todos os módulos
5. **Error Handling** - Exception hierarchy (`AppException` → specific errors)
6. **Type Safety** - Full type hints, Pydantic models for requests/responses
7. **Async First** - All I/O operations async (database, HTTP, Redis, S3)

### Adding a New Module
1. Create module in `app/modules/<name>/` with `router.py`, `service.py`, `schemas.py`, `models.py` (if needed)
2. Register router in `app/main.py`
3. Add tests in `tests/`
4. Update OpenAPI tags

### Adding a New Rule
1. Create rule class in `app/services/rules_critical.py` extending `BaseRule`
2. Define `relevance_tags` for smart filtering
3. Register in `create_engine_v2()` factory
4. Add test cases in `tests/test_rules_critical.py`
5. Update reference data in `app/data/` if needed

### Working with Celery Tasks
- Define tasks in `app/tasks/`
- Use `app.core.celery_app.celery_app` for task decorator
- For long-running tasks: use `acks_late=True`, `reject_on_worker_lost=True`
- Monitor with Flower (`poetry run flower`)

### Database Changes
1. Modify `prisma/schema.prisma`
2. Run `poetry run prisma db push` (dev) or `prisma migrate dev` (with migration)
3. Run `poetry run prisma generate` to update client
4. Update affected services/modules

## Notes for AI Agents

- **Main backend is Python FastAPI** - The NestJS backend in `../packages/backend/` is a separate/alternative implementation
- Frontend (React) in `../packages/frontend/` proxies `/api` to `localhost:8000`
- Prisma Client Python provides type-safe database access
- All datetime handling in UTC, timezone-aware
- Money values stored as `Decimal` (avoid float)
- XML parsing uses `lxml` with namespace awareness for CT-e/NF-e
- PDF generation uses ReportLab (blocking - consider threadpool for large docs)
- Email templates use Jinja2 with both HTML and text versions
- Redis used for: Celery broker, cache (Cards #04, #05 DONE), rate limiting
- MinIO/S3 for document storage (XML originals, generated PDFs)

---

*This agent owns backend implementation. After each card: update this file, move card, commit.*