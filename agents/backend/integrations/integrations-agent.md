---
name: averta-backend-integrations-agent
description: Specialized agent for External Integrations - Webhooks, ERP/TMS, EDI, Email, S3/MinIO
tools: Read, Write, Edit, Glob, Grep, PowerShell, ListAgents
---

# AvertaSaaS Backend Integrations Agent

> **Specialization:** Webhooks, external system integrations (ERP, TMS), EDI, email, storage
> **Location:** `backend/`
> **Cards:** #18 (Webhooks)
> **Related Agents:** `core`, `rules-engine`

## Project Context

**Services:** `app/services/email_service.py`, `app/services/storage.py`
**Tasks:** `app/tasks/` - Celery async dispatch
**Templates:** `app/templates/emails/` - 7 Jinja2 templates

## Current Integrations

### ✅ Email (SendGrid)
- 7 templates: discrepancy_alert, contest_created, weekly_report, contract_expiring, payment_received, welcome, password_reset
- HTML + Text versions
- Async via Celery

### ✅ Storage (MinIO/S3)
- CRUD + presigned URLs
- Document upload (XML originals)
- PDF generation storage

### 🔄 Webhooks (Card #18 - Sprint 3, M, HIGH)

**Events to Implement:**
| Event | Trigger | Payload Key Fields |
|-------|---------|-------------------|
| `discrepancy.detected` | Rules engine finds discrepancy | discrepancy_id, rule_code, severity, difference, document_id, carrier |
| `contest.created` | Contest created from discrepancies | contest_id, items[], carrier, total_amount |
| `contest.updated` | Status change (negotiation) | contest_id, old_status, new_status, carrier |
| `payment.received` | Payment registered | payment_id, contest_id, amount, carrier |

**Implementation Tasks:**
- Prisma model `Webhook` (url, events[], secret, is_active, retry_count)
- Service `webhook_service.py` - async dispatch via Celery
- HMAC SHA256 signature verification
- Retry: exponential backoff (1m, 5m, 15m, 1h, 6h) max 5
- Dead letter queue → log + alert
- API CRUD: POST/GET/PATCH/DELETE /webhooks
- Frontend: Webhook management page

## Webhook Payload Example

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

## Adding a New Webhook Event

```python
# 1. Add event to Webhook model events enum
# 2. Create payload builder in webhook_service.py
async def build_discrepancy_payload(discrepancy: Discrepancy) -> dict:
    return {
        "event": "discrepancy.detected",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {...}
    }

# 3. Dispatch in relevant service (e.g., rules_engine after evaluate_all)
await webhook_service.dispatch("discrepancy.detected", payload)

# 4. Celery task handles retry + DLQ
```

## Future Integrations (Roadmap)
- **EDI/Integração TMS** - Parser layout Carga/Descarga
- **Multi-modal Freight** - Aéreo, marítimo, ferroviário
- **GraphQL Gateway** - Apollo/Strawberry federation
- **Event Sourcing** - Kafka audit trail

## Testing
```bash
cd backend
poetry run pytest tests/test_webhooks.py -v  # When created
```

## Quality Gates
```bash
poetry run lint
poetry run typecheck
poetry run test-cov
```

---

*Specialized for external integrations. Delegates core backend to core agent.*