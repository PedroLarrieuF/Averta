---
id: 20
title: "Global Soft Delete (deleted_at + BaseService Filter)"
priority: medium
type: tech-debt
agent: backend
sprint: 3
estimate: S
status: backlog
created: 2026-11-01
reviewed_by: techlead
---

# Card 20: Global Soft Delete

## Contexto
Adicionar `deleted_at` em todos models + filtro automático no BaseService. TD curto prazo.

## Definition of Ready
- [ ] Prisma schema update: adicionar `deleted_at DateTime?` em todos models
- [ ] BaseService pattern identificado

## Tasks
- [ ] Migration Prisma: add `deleted_at` em 25 models
- [ ] Atualizar `BaseService` (se existe) ou criar trait/mixin:
  - `find_many`: auto-filter `deleted_at: null`
  - `find_unique`: auto-filter
  - `delete`: soft delete (update deleted_at=now)
  - `hard_delete`: opcional para admin
  - `restore`: update deleted_at=null
- [ ] Endpoints: `DELETE` = soft, `DELETE /hard` = hard (admin only)
- [ ] Unique constraints: permitir reuso de email/cnpj após soft delete (partial index)
- [ ] Frontend: "Lixeira" view, restaurar, excluir permanentemente
- [ ] Testes: soft delete, restore, hard delete, unique constraints

## Prisma Partial Index Example
```prisma
model User {
  email String @unique
  deletedAt DateTime?
  
  @@index([email, deletedAt]) // Partial unique: WHERE deletedAt IS NULL
}
```

## Acceptance Criteria
- [ ] DELETE não remove dados, marca deleted_at
- [ ] Listagens não mostram deletados
- [ ] Restaurar funciona
- [ ] Hard delete só admin
- [ ] Unique constraints respeitam soft delete

## Referências
- `TECHLEAD_REVIEW.md` - Curto prazo
- `backend/prisma/schema.prisma` - todos models