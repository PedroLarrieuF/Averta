---
id: 40
title: "API Public: OpenAPI 3.1 Spec v1"
priority: critical
type: feature
agent: backend
sprint: 1
estimate: L
status: ready
created: 2026-11-04
reviewed_by: techlead
---

# Card 40: API Public - OpenAPI 3.1 Spec v1

## Contexto
Criar a especificação OpenAPI 3.1 completa como **source of truth** para a API pública AvertaSaaS. Serve para: documentação, geração de SDKs, validação, API Gateway configuração.

## Decisões Arquiteturais (Já Definidas)
- **Auth**: API Keys + JWT (RS256)
- **Gateway**: AWS API Gateway (REST API)
- **Versioning**: URL path `/v1/`
- **Ambientes**: Sandbox + Production
- **Error Format**: RFC 9457 (Problem Details)
- **Monetização**: Success-based (5% M1 → 10% M2+)

## Tasks

### 1. Estrutura Base do Spec
- [ ] `docs/openapi/v1.yaml` - Arquivo principal
- [ ] `docs/openapi/components/` - Schemas, parameters, responses, securitySchemes reutilizáveis
- [ ] `docs/openapi/paths/` - Um arquivo por resource (discrepancies.yaml, documents.yaml, etc.)

### 2. Security Schemes
```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: "API Key para autenticação server-to-server"
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: "JWT RS256 emitido pelo Authorizer Lambda"
```

### 3. Resource: Discrepancies
```yaml
/v1/discrepancies:
  get:
    summary: List discrepancies with filters
    security: [{ ApiKeyAuth: [] }, { BearerAuth: [] }]
    parameters:
      - $ref: '#/components/parameters/page'
      - $ref: '#/components/parameters/limit'
      - name: status
        in: query
        schema: { type: string, enum: [PENDING, IN_REVIEW, APPROVED, REJECTED, UNDER_REVIEW] }
      - name: severity
        in: query
        schema: { type: string, enum: [LOW, MEDIUM, HIGH, CRITICAL] }
      - name: carrier_id
        in: query
        schema: { type: string, format: uuid }
      - name: rule_code
        in: query
        schema: { type: string }
      - name: date_from
        in: query
        schema: { type: string, format: date }
      - name: date_to
        in: query
        schema: { type: string, format: date }
    responses:
      '200':
        description: Paginated list
        content:
          application/json:
            schema: { $ref: '#/components/schemas/DiscrepancyListResponse' }
      '401': { $ref: '#/components/responses/Unauthorized' }
      '429': { $ref: '#/components/responses/RateLimited' }
  post:
    summary: Create discrepancy (internal use)
    # ... bulk review endpoint separate
```

### 4. Resource: Documents
- POST `/v1/documents/upload` (multipart/form-data)
- GET `/v1/documents` (list with filters)
- GET `/v1/documents/{id}` (detail + download links)
- POST `/v1/documents/{id}/reprocess`
- GET `/v1/documents/{id}/download` (XML/PDF original)

### 5. Resource: Contests
- CRUD completo
- POST `/v1/contests/{id}/send`
- PATCH `/v1/contests/{id}/negotiate`
- POST `/v1/contests/{id}/payments`

### 6. Resource: Reports
- GET `/v1/reports/dashboard` (metrics)
- GET `/v1/reports/export` (PDF/Excel)
- POST `/v1/reports/schedule`

### 7. Resource: Settings (Admin only)
- Companies, Users, Carriers, Contracts, Notifications CRUD

### 8. Webhooks Section
```yaml
webhooks:
  discrepancy.created:
    post:
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/WebhookDiscrepancyCreated' }
  discrepancy.updated: ...
  contest.status_changed: ...
  document.processed: ...
  report.generated: ...
```

### 9. Common Components
- **Pagination**: page, limit, total, has_more
- **Error Responses**: 400, 401, 403, 404, 422, 429, 500 (RFC 9457)
- **Rate Limit Headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- **Idempotency**: Idempotency-Key header support

### 10. Sandbox vs Production
- Servers array com URLs sandbox e production
- Exemplos de dados mockados para sandbox

## Acceptance Criteria
- [ ] Spec válido (openapi-spec-validator passa)
- [ ] Gera SDKs TypeScript/Python/Go sem erros
- [ ] Importa no AWS API Gateway sem erros
- [ ] Documentação renderizada no Scalar/Redoc completa
- [ ] Todos endpoints atuais cobertos
- [ ] Versionamento `/v1/` explícito em todos paths

## Referências
- `backend/README.md` - Endpoints atuais
- `docs/openapi/` - Diretório para spec
- RFC 9457 - Problem Details for HTTP APIs
- AWS API Gateway OpenAPI extensions

## Dependencies
- Nenhuma (primeiro card da API pública)