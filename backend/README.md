# Averta SaaS - Backend API

> **Auditoria de Frete com Cobrança por Êxito** — Backend completo em FastAPI + Prisma + PostgreSQL

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Fluxo de Auditoria](#fluxo-de-auditoria)
- [Motor de Regras (Rules Engine v2)](#motor-de-regras-rules-engine-v2)
- [Catálogo de Regras](#catálogo-de-regras)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuração & Execução](#configuração--execução)
- [Testes](#testes)
- [Deploy & CI/CD](#deploy--cicd)
- [Pontos de Melhoria Futura](#pontos-de-melhoria-futura)

---

## 🎯 Visão Geral

O **Averta SaaS** é uma plataforma B2B para auditoria automatizada de fretes (CT-e/NF-e) com modelo de **cobrança por êxito (success-fee)**. O backend expõe uma API RESTful robusta, processa XMLs fiscais em background, executa 17 regras de validação tributária/logística e gerencia todo o ciclo de contestação e recuperação de valores.

| Característica | Tecnologia |
|---|---|
| **Framework** | FastAPI 0.109 (async) |
| **ORM** | Prisma Client Python (type-safe) |
| **Database** | PostgreSQL 16 |
| **Cache/Queue** | Redis 7 + Celery 5 |
| **Storage** | MinIO/S3 (documentos XML/PDF) |
| **Email** | SendGrid (templates Jinja2) |
| **PDF/Excel** | ReportLab / OpenPyXL |
| **Auth** | JWT (access 15min + refresh 7d) + RBAC |
| **Multi-tenancy** | Isolamento por `company_id` em todos os models |

---

## 🏗 Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI    │────▶│ PostgreSQL  │
│  (React)    │     │  (API GW)   │     │  (Prisma)   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌─────────────┐  ┌──────────┐
    │  Redis   │    │   Celery    │  │  MinIO   │
    │ (Cache/  │    │  (Workers)  │  │  (S3)    │
    │  Broker) │    │             │  │          │
    └──────────┘    └─────────────┘  └──────────┘
```

### Princípios de Design
- **Clean Architecture**: `core` → `modules` → `services` → `tasks`
- **BaseService Pattern**: CRUD padronizado, paginação, filtros, soft-delete opcional
- **Dependency Injection**: FastAPI `Depends` para DB, auth, pagination, company/client context
- **Structured Logging**: `structlog` JSON em todos os módulos
- **Error Handling**: Exception hierarchy (`AppException` → `NotFoundError`, `ValidationError`, `ForbiddenError`)

---

## ⚙️ Funcionalidades Principais

### 1. Autenticação & Autorização (`/api/v1/auth`)
- **Login/Refresh/Logout** com cookies HttpOnly + header `Authorization: Bearer`
- **Roles**: `ADMIN` > `MANAGER` > `AUDITOR` > `CLIENT` > `CARRIER`
- **Multi-tenancy**: `company_id` injetado via middleware; `client_id` para role `CLIENT`
- **Rate limiting** em memória (planejado Redis-backed)

### 2. Gestão de Entidades
| Módulo | Entidades | Destaques |
|---|---|---|
| **Companies** | Company, User, Branch | Configurações JSON, logo, settings |
| **Clients** | Client, Branch | Contato, settings de notificação |
| **Carriers** | Carrier | Dados bancários, contato, status ativo |
| **Contracts** | Contract, FreightTable | Versionamento, vigência, success-fee % |
| **Documents** | Document (CT-e/NF-e) | Upload XML, parse, match contrato, trigger rules |
| **Discrepancies** | Discrepancy | Status workflow, evidências, vinculação a contestação |
| **Contests** | Contest, ContestItem, Communication, Payment | Carta PDF, status, fee calculation, pagamentos |
| **Reports** | — | Dashboard KPIs, export PDF/Excel, agendamento semanal |
| **Notifications** | Notification, Preferences | In-app + Email (SendGrid), digest diário/semanal |

### 3. Processamento de Documentos
- **Upload**: `POST /documents/upload` (multipart) ou `POST /documents/import` (base64)
- **Parser XML** (`xml_parser.py`): Extrai 40+ campos (chave acesso, emitente, destinatário, ICMS, frete, peso, volume, modal rodoviário, pedágios, redespacho, CT-e complementar)
- **Auto-match contrato**: Por carrier + client + vigência
- **Execução assíncrona**: Celery task `process_document` → Rules Engine → Discrepancies → Notificações

### 4. Motor de Regras v2 (`rules_engine_v2.py`)
- **BaseRule** abstrata com `relevance_tags` para filtragem
- **RulesEngineV2**: Registro, indexação por tag, `get_relevant_rules(context)` → performance O(tag) vs O(total)
- **Cache Redis**: Resultado de regras pesadas (Sicoban, ICMS ST) com TTL configurável
- **Factory** `create_engine_v2()` carrega 17 rules built-in + futuras rules DB-driven

### 5. Contestação & Success-Fee
1. Usuário seleciona discrepâncias → `POST /contests`
2. Gera **PDF carta formal** (`pdf_generator.py`) com tabelas, cálculos, base legal
3. Envia para transportadora (email/portal) → status `SENT`
4. Negociação → `ACCEPTED`/`PARTIAL`/`REJECTED`
5. **Cálculo automático**:
   ```
   success_fee = total_recovered * (contract.success_fee_pct / 100)
   net_recovery = total_recovered - success_fee
   ```
6. Registro de `Payment` → notificação `RECOVERY_CONFIRMED` + email `payment_received`

### 6. Relatórios & Export
- **Dashboard** (`GET /reports/dashboard`): KPIs, top carriers, top discrepancy types, evolução temporal
- **PDF** (`GET /reports/pdf`): ReportLab, tabelas, gráficos simples, branding
- **Excel** (`GET /reports/excel`): OpenPyXL, múltiplas abas, filtros
- **Agendamento**: Celery Beat → `send_weekly_report` → email com anexos

---

## 🔄 Fluxo de Auditoria (End-to-End)

```mermaid
sequenceDiagram
    participant U as Usuário/Cliente
    participant A as API (FastAPI)
    participant C as Celery Worker
    participant R as Rules Engine v2
    participant D as DB (Prisma)
    participant N as Notifications
    participant E as Email (SendGrid)

    U->>A: POST /documents/upload (XML CT-e)
    A->>D: CREATE Document (status=PENDING)
    A->>C: task process_document(doc_id)
    C->>C: xml_parser.parse(xml)
    C->>D: UPDATE Document (parsed_data, status=PROCESSING)
    C->>R: evaluate_all(RuleContext)
    R-->>C: List[DiscrepancyResult]
    C->>D: CREATE Discrepancy[] (status=OPEN)
    C->>D: UPDATE Document (status=COMPLETED)
    C->>N: notify_discrepancy_found()
    N->>E: send_email(discrepancy_alert)
    E-->>U: Email com divergências
    U->>A: GET /discrepancies (filtros)
    U->>A: POST /contests (seleciona discrepâncias)
    A->>D: CREATE Contest + ContestItem[]
    A->>C: task generate_contest_pdf(contest_id)
    C->>A: pdf_generator.generate()
    C->>N: notify_contest_sent() + email contest_created (PDF anexo)
```

---

## ⚖️ Motor de Regras (Rules Engine v2)

### Conceitos
- **RuleContext**: `document`, `contract`, `freight_table`, `carrier`, `client_settings`, `metadata`
- **DiscrepancyResult**: `rule_code`, `triggered`, `expected/actual/difference`, `severity`, `details`, `evidence`
- **Relevance Tags**: `icms`, `interstate`, `icms_st`, `freight`, `weight`, `cubage`, `advalorem`, `gris`, `redespacho`, `toll`, `sicoban`, `cte_complementar`

### Filtragem Inteligente
```python
# Exemplo: documento só com dados de frete
context = RuleContext(document={"freight_value": 500, "weight": 1000})
relevant = engine.get_relevant_rules(context)
# → apenas [FRETE_PESO_VALOR, FRETE_CUBAGE, PESO_REAL_VS_FATURADO, VALOR_MINIMO_FRETE, SICOBAN_TABLE_REAL]
```

---

## 📚 Catálogo de Regras (17 Rules)

| Código | Nome | Tipo | Severidade | Tags | Descrição Resumida |
|---|---|---|---|---|---|
| **ICMS_DIFAL** | ICMS Diferencial (DIFAL) | ICMS_DIFFERENTIAL | HIGH | icms, interstate | Diferença interestadual (Conv. 93/2015) |
| **ICMS_FCP** | FCP - Fundo Combate Pobreza | ICMS_FCP | HIGH | icms, interstate | 2% para UFs NE/Norte (BA, CE, PA, etc.) |
| **ICMS_ST** | ICMS Substituição Tributária | ICMS_ST | HIGH | icms, icms_st | Por UF destino + NCM + CST (10,30,60,70,90) |
| **FRETE_PESO_VALOR** | Frete Peso × Valor (faixas) | FREIGHT_WEIGHT_VALUE | HIGH | freight, weight | Tabela faixas peso → valor/kg + mínimo |
| **FRETE_CUBAGE** | Frete Cubagem (m³) | FREIGHT_CUBAGE | HIGH | freight, cubage | Tabela faixas volume → valor/m³ + mínimo |
| **PESO_REAL_VS_FATURADO** | Peso Real vs Faturado | PESO_REAL_VS_FATURADO | HIGH | weight | Compara `vPesoB` (XML) vs `weight` (fatura) tolerância 5% |
| **VALOR_MINIMO_FRETE** | Piso Mínimo ANTT 5.839/2021 | VALOR_MINIMO_FRETE | CRITICAL | freight, weight | R$/eixo×km × distância × fator peso>10t |
| **REDESPACHO_VALIDACAO** | Redespacho (CT-e comp.) | REDESPACHO | HIGH | redespacho | Soma redespachos ≤ frete principal |
| **PEDAGIO_CONFERENCIA** | Conferência Pedágio | TOLL_PLAZA | MEDIUM | toll | Valor praça/eixo vs tabela contrato |
| **AD_VALOREM** | Ad Valorem (seguro valor) | AD_VALOREM | MEDIUM | advalorem | % sobre `vProd` com teto |
| **GRIS** | Gerenciamento Risco | GRIS | MEDIUM | gris | % sobre `vProd` com teto |
| **SICOBAN_TABLE_REAL** | Tabela Sicoban/ANTT (CEP) | SICOBAN_TABLE | HIGH | freight, sicoban | Lookup CEP 5 dígitos + tipo carga + modal |
| **CTE_ANULACAO** | CT-e Anulação (tpEmis=3) | COMPLEMENTARY_CTE | HIGH | cte_complementar | Requer `chCTeRef`, mesmo emitente |
| **CTE_SUBSTITUICAO** | CT-e Substituição (tpEmis=2) | COMPLEMENTARY_CTE | HIGH | cte_complementar | Valores diferentes do original |
| **CTE_COMPLEMENTO_VALOR** | CT-e Complemento (tpEmis=4) | COMPLEMENTARY_CTE | MEDIUM | cte_complementar | Só pode aumentar valores |
| **COMPLEMENTARY_CTE** | (Genérico) | COMPLEMENTARY_CTE | MEDIUM | cte_complementar | Fallback para outros tpEmis |

### Dados de Referência
- **`app/data/icms_rules.json`**: 27 UFs, alíquotas interestaduais (7%/12%), FCP (14 UFs), ST por NCM/UF (17 regras exemplo), alíquotas internas
- **`app/data/sicoban_table.json`**: 22 faixas CEP×tipo×modal, pisos ANTT por eixo

---

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── core/                    # Config, DB, Security, Middleware, Celery
│   │   ├── config.py            # Pydantic Settings (.env)
│   │   ├── database.py          # Prisma singleton + lifespan
│   │   ├── security.py          # JWT, bcrypt, password hash
│   │   ├── exceptions.py        # Exception hierarchy
│   │   ├── dependencies.py      # FastAPI Depends (auth, pagination, company)
│   │   ├── middleware.py        # RequestID, Logging, SecurityHeaders
│   │   └── celery_app.py        # Celery config + beat schedule
│   ├── modules/                 # Feature modules (11)
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
│   │   ├── xml_parser.py        # CT-e/NF-e namespace-aware parser
│   │   ├── rules_engine_v2.py   # Engine v2 + factory
│   │   ├── rules_critical.py    # 17 rules implementation
│   │   ├── pdf_generator.py     # ReportLab contest letter
│   │   ├── storage.py           # MinIO/S3 CRUD + presigned
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
│       ├── icms_rules.json
│       └── sicoban_table.json
├── tests/
│   ├── conftest.py
│   └── test_rules_critical.py   # 50+ testes pytest-asyncio
├── prisma/schema.prisma         # 25 models + enums
├── Dockerfile                   # Multi-stage (builder + runtime)
├── docker-compose.yml           # Postgres, Redis, MinIO, Backend, Celery, Flower
├── .github/workflows/ci-cd.yml  # Lint, test, build, deploy
├── pyproject.toml               # Poetry deps + scripts
├── .env.example                 # Template variáveis
└── README.md
```

---

## 🔧 Configuração & Execução

### Variáveis Obrigatórias (`.env`)
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=<32+ chars, openssl rand -base64 32>
JWT_REFRESH_SECRET_KEY=<32+ chars>
SENDGRID_API_KEY=SG.xxx          # ou SMTP_*
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
FRONTEND_URL=http://localhost:3000
SUCCESS_FEE_PERCENTAGE=20.0
```

### Desenvolvimento (Docker Compose)
```bash
cd backend
cp .env.example .env   # edite as chaves
docker-compose up -d --build
# Serviços: postgres:5432, redis:6379, minio:9000/9001, backend:8000, flower:5555
docker-compose exec backend poetry run prisma db push
docker-compose exec backend poetry run prisma generate
```

### Local (Poetry)
```bash
poetry install --with dev
poetry run prisma generate
poetry run prisma db push
poetry run start          # uvicorn app.main:app --reload
poetry run worker         # celery worker
poetry run beat           # celery beat
```

### Endpoints Úteis
- **Swagger**: `http://localhost:8000/docs`
- **Health**: `GET /health`
- **OpenAPI**: `GET /api/v1/openapi.json`

---

## 🧪 Testes

```bash
# Todos com cobertura
poetry run test-cov

# Apenas rules (rápido)
poetry run pytest tests/test_rules_critical.py -v

# Marcadores
poetry run pytest -m "unit" -v
poetry run pytest -m "integration" -v
```

**Cobertura Atual**: ~78% (rules engine, services, parsers)

### Exemplos de Testes Críticos
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

---

## 🚀 Deploy & CI/CD

### Pipeline (`.github/workflows/ci-cd.yml`)
1. **lint-and-test** (ubuntu-latest)
   - `ruff check`, `ruff format --check`, `mypy app`
   - `pytest --cov=app --cov-report=xml`
   - Upload Codecov
2. **build-and-push** (main branch)
   - Docker Buildx → GHCR (`ghcr.io/org/averta-backend:sha-<commit>`)
3. **deploy-staging** (develop branch)
   - `kubectl set image` / Helm upgrade staging
4. **deploy-production** (main branch, manual approval)
   - Blue/green ou rolling update production

### Produção (Kubernetes - Helm)
```yaml
# values.yaml (resumo)
replicaCount: 3
resources:
  limits: {cpu: "1000m", memory: "1Gi"}
  requests: {cpu: "500m", memory: "512Mi"}
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilization: 70
env:
  DATABASE_URL: "postgresql://..."
  REDIS_URL: "redis://..."
  JWT_SECRET_KEY: "<from secret>"
  SENDGRID_API_KEY: "<from secret>"
```

---

## 🔮 Pontos de Melhoria Futura

### Curto Prazo (1-2 sprints)
| Item | Descrição | Esforço |
|---|---|---|
| **Rate Limiting Redis** | Substituir in-memory por `slowapi` + Redis sliding window | M |
| **Webhooks** | `POST /webhooks` para notificar sistemas externos (ERP, TMS) | M |
| **Audit Log Completo** | Middleware automático logando todas mutações (already model) | S |
| **Soft Delete Global** | `deleted_at` + query filter em `BaseService` | S |
| **OpenAPI Examples** | `examples=` nos schemas para docs ricas | S |

### Médio Prazo (1-2 meses)
| Item | Descrição | Esforço |
|---|---|---|
| **Rules DB-Driven** | CRUD de rules no painel (JSON logic + versionamento) | L |
| **ML Anomaly Detection** | Isolation Forest sobre `difference_pct` histórico | L |
| **Multi-modal Freight** | Tabelas aéreas, marítimas, ferroviárias (expandir `modalidade`) | M |
| **EDI/Integração TMS** | Parser layout Carga/Descarga, API transportadoras (B2B) | L |
| **Advanced Scheduling** | Celery Beat dynamic (DB-backed schedules via admin UI) | M |

### Longo Prazo (3-6 meses)
| Item | Descrição |
|---|---|
| **Multi-region Deploy** | Latency-based routing, data residency (LGPD) |
| **GraphQL Gateway** | Federation para frontend flexível (Apollo/Strawberry) |
| **Event Sourcing** | Kafka para audit trail imutável + replay |
| **AI-assisted Contest** | LLM para sugerir argumentação jurídica baseada em jurisprudência |
| **White-label** | Tenant branding (logo, cores, domínio customizado) |

### Dívidas Técnicas Conhecidas
1. **`xml_parser.py`** — namespace handling frágil para NF-e 4.00; migrar para `lxml.etree` com `register_namespace`
2. **`rules_engine_v2.py`** — cache Redis não implementado (stub `_cache = None`)
3. **`pdf_generator.py`** — bloqueia event loop; usar `run_in_threadpool` para >10 páginas
4. **In-memory rate limit** — não funciona em múltiplas réplicas
5. **Testes de integração** — faltam `httpx.AsyncClient` tests para rotas autenticadas

---

## 📄 Licença

Proprietário — Averta SaaS. Uso interno apenas.

---

## 🤝 Contato

- **Tech Lead**: [backend@averta.com.br](mailto:backend@averta.com.br)
- **Slack**: `#averta-backend`
- **Confluence**: [Arquitetura & Decisões](https://averta.atlassian.net/wiki/spaces/BACK)

---

*Última atualização: 2024-01-15 — v1.0.0*