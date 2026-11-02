---
id: 18
title: "Webhooks for External Systems (ERP, TMS)"
priority: high
type: feature
agent: backend
sprint: 3
estimate: M
status: backlog
created: 2026-11-01
reviewed_by: techlead
---

# Card 18: Webhooks for External Systems

## Contexto
Roadmap curto prazo. Notificar sistemas externos (ERP, TMS) sobre eventos: discrepância detectada, contestação criada, pagamento recebido.

## Definition of Ready
- [ ] Eventos definidos: discrepancy.detected, contest.created, contest.updated, payment.received
- [ ] Payload schema por evento
- [ ] Retry policy + dead letter queue

## Tasks
- [ ] Model `Webhook` no Prisma (url, events[], secret, is_active, retry_count)
- [ ] Service `webhook_service.py` - dispatch assíncrono via Celery
- [ ] Assinatura HMAC (SHA256) no payload para verificação
- [ ] Retry: exponential backoff (1m, 5m, 15m, 1h, 6h) max 5 tentativas
- [ ] Dead letter: após falhas -> log + alerta
- [ ] API CRUD: POST/GET/PATCH/DELETE /webhooks
- [ ] Frontend: Webhook management page (Settings)
- [ ] Testes: delivery, retry, signature verification, DLQ

## Event Payload Example
```json
{
  "event": "discrepancy.detected",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "discrepancy_id": "abc123",
    "rule_code": "ICMS_DIFAL",
    "severity": "HIGH",
    "difference": 150.00,
    "document_id": "doc456",
    "carrier": { "id": "car1", "name": "Transportadora XYZ" }
  }
}
```

## Acceptance Criteria
- [ ] Webhooks entregues com < 5s latência
- [ ] Retry automático com backoff
- [ ] Assinatura válida verificável pelo receptor
- [ ] DLQ alerta no Slack/email
- [ ] Frontend gerencia webhooks

## Referências
- `TECHLEAD_REVIEW.md` - Curto prazo
- `backend/app/tasks/` - Celery pattern