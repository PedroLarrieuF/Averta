---
id: 41
title: "API Public: API Key Model & Infrastructure"
priority: critical
type: feature
agent: backend
sprint: 1
estimate: M
status: ready
created: 2026-11-04
reviewed_by: techlead
---

# Card 41: API Public - API Key Model & Infrastructure

## Contexto
Implementar o modelo de dados e infraestrutura para API Keys: criação, hash, validação, scopes, tiers, expiração, rotação.

## Decisões
- **Hash**: Argon2id (não armazenar plain text)
- **Prefixo visível**: `avsk_` + 8 chars (para identificação no dashboard)
- **Scopes**: `discrepancies:read`, `discrepancies:write`, `documents:read`, `documents:write`, `contests:read`, `contests:write`, `reports:read`, `settings:read`, `settings:write`, `webhooks:read`, `webhooks:write`, `admin:all`
- **Tiers**: `free` (100 req/min), `pro` (1000 req/min), `enterprise` (10000 req/min)
- **Expiração**: Opcional (default 1 ano), notificação 30/7/1 dia antes

## Tasks

### 1. Database Migration
```sql
-- api_keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,        -- Argon2id hash
    key_prefix VARCHAR(12) NOT NULL,       -- "avsk_abc12345"
    scopes TEXT[] NOT NULL DEFAULT '{}',   -- Array of scope strings
    tier VARCHAR(20) NOT NULL DEFAULT 'free', -- free, pro, enterprise
    rate_limit_override INTEGER,           -- Custom rate limit (req/min)
    expires_at TIMESTAMPTZ,                -- NULL = never expires
    last_used_at TIMESTAMPTZ,
    usage_count BIGINT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    company_id UUID REFERENCES companies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX idx_api_keys_company ON api_keys(company_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active) WHERE deleted_at IS NULL;
```

### 2. API Key Service (`services/api_key_service.py`)
```python
class APIKeyService:
    async def create_key(
        self,
        name: str,
        scopes: list[str],
        tier: str = "free",
        expires_in_days: int = 365,
        company_id: UUID,
        created_by: UUID
    ) -> tuple[APIKey, str]:  # Returns (model, plain_key)
        # Generate: avsk_ + 32 random chars
        # Hash with Argon2id
        # Return plain key ONLY once

    async def validate_key(self, plain_key: str) -> APIKey | None:
        # Find by prefix, verify Argon2id hash
        # Update last_used_at, usage_count

    async def rotate_key(self, key_id: UUID) -> tuple[APIKey, str]:
        # Invalidate old, create new with same scopes/tier

    async def revoke_key(self, key_id: UUID) -> None:
        # Soft delete (deleted_at = now)

    async def list_keys(self, company_id: UUID, include_revoked: bool = False) -> list[APIKey]:
        # For dashboard

    async def get_usage_stats(self, key_id: UUID, days: int = 30) -> UsageStats:
        # From usage_metrics table
```

### 3. Scopes & Permissions Matrix
| Scope | Resources | Actions |
|-------|-----------|---------|
| `discrepancies:read` | GET /discrepancies, GET /discrepancies/{id}, GET /discrepancies/summary | List, Detail, Summary |
| `discrepancies:write` | PATCH /discrepancies/bulk, POST /discrepancies/{id}/review | Bulk update, Review |
| `documents:read` | GET /documents, GET /documents/{id}, GET /documents/{id}/download | List, Detail, Download |
| `documents:write` | POST /documents/upload, POST /documents/{id}/reprocess | Upload, Reprocess |
| `contests:read` | GET /contests, GET /contests/{id} | List, Detail |
| `contests:write` | POST /contests, POST /contests/{id}/send, PATCH /contests/{id}/negotiate, POST /contests/{id}/payments | Create, Send, Negotiate, Pay |
| `reports:read` | GET /reports/dashboard, GET /reports/export, GET /reports/schedule | Dashboard, Export, Schedule |
| `settings:read` | GET /settings/* | List all settings |
| `settings:write` | POST/PATCH/DELETE /settings/* | Manage settings |
| `webhooks:read` | GET /webhooks, GET /webhooks/{id}/deliveries | List, View deliveries |
| `webhooks:write` | POST/PATCH/DELETE /webhooks, POST /webhooks/{id}/replay | Manage, Replay |
| `admin:all` | All endpoints | Full access |

### 4. Tier Configuration
```python
TIER_CONFIG = {
    "free": {
        "rate_limit_per_minute": 100,
        "rate_limit_per_day": 10000,
        "max_keys": 2,
        "webhooks_max": 3,
        "sandbox_only": True
    },
    "pro": {
        "rate_limit_per_minute": 1000,
        "rate_limit_per_day": 100000,
        "max_keys": 10,
        "webhooks_max": 20,
        "sandbox_only": False
    },
    "enterprise": {
        "rate_limit_per_minute": 10000,
        "rate_limit_per_day": 1000000,
        "max_keys": 50,
        "webhooks_max": 100,
        "sandbox_only": False,
        "custom_sla": True
    }
}
```

### 5. API Endpoints (Internal/Admin)
- POST `/admin/api-keys` - Criar key
- GET `/admin/api-keys` - Listar keys
- GET `/admin/api-keys/{id}` - Detalhes + usage
- POST `/admin/api-keys/{id}/rotate` - Rotacionar
- DELETE `/admin/api-keys/{id}` - Revogar
- GET `/admin/api-keys/{id}/usage` - Métricas de uso

### 6. Usage Metrics Table
```sql
CREATE TABLE api_key_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID REFERENCES api_keys(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    request_size_bytes BIGINT,
    response_size_bytes BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usage_key_time ON api_key_usage(api_key_id, created_at);
CREATE INDEX idx_usage_endpoint ON api_key_usage(endpoint);
```

## Acceptance Criteria
- [ ] Migration roda sem erro
- [ ] Criar key retorna plain key apenas uma vez
- [ ] Validação Argon2id funciona
- [ ] Scopes enforçados no authorizer
- [ ] Rate limit por tier configurável
- [ ] Rotação invalida key antiga
- [ ] Métricas de uso registradas
- [ ] Testes unitários > 90% coverage

## Referências
- Card 40 (OpenAPI Spec) - Scopes definidos lá
- Card 42 (JWT Authorizer) - Consome este model
- Card 43 (API Gateway) - Usage plans baseados em tier