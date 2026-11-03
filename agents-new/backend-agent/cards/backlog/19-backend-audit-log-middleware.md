---
id: 19
title: "Complete Audit Log Middleware (Auto-log all Mutations)"
priority: medium
type: tech-debt
agent: backend
sprint: 3
estimate: S
status: backlog
created: 2026-11-01
reviewed_by: techlead
---

# Card 19: Complete Audit Log Middleware

## Contexto
Model `AuditLog` existe no Prisma mas middleware automático não implementado. TD curto prazo.

## Definition of Ready
- [ ] Model AuditLog pronto (companyId, userId, action, entityType, entityId, oldData, newData, ip, ua)
- [ ] Middleware pattern estabelecido

## Tasks
- [ ] Criar `app/core/audit_middleware.py` - intercepta requests mutantes (POST/PATCH/DELETE)
- [ ] Capturar: user do token, company_id, body antes/depois (para PATCH/DELETE)
- [ ] Filtrar campos sensíveis (passwordHash, tokens, secrets)
- [ ] Batch insert para performance (buffer + flush periódico)
- [ ] Integrar no `main.py` middleware stack
- [ ] API: GET /audit-logs com filtros (entity, user, date range)
- [ ] Frontend: Audit Log page (Settings > Auditoria)
- [ ] Testes: middleware loga create/update/delete

## Implementation Sketch
```python
# app/core/audit_middleware.py
class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in ("POST", "PATCH", "PUT", "DELETE"):
            return await call_next(request)
        
        # Capture request body
        body = await request.body()
        # ... process response, capture changes
        # Log to AuditLog table
```

## Acceptance Criteria
- [ ] Todas mutações logadas automaticamente
- [ ] Dados sensíveis filtrados
- [ ] Performance impact < 5ms
- [ ] Queryable via API
- [ ] Frontend exibe timeline

## Referências
- `TECHLEAD_REVIEW.md` - Curto prazo
- `backend/prisma/schema.prisma` - model AuditLog