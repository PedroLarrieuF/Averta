# AvertaSaaS Backend Agents

## Folder Structure

```
agents/backend/
├── core/                    # General backend development
│   └── core-agent.md        # Modules, API, DB, Celery, testing
├── rules-engine/            # Rules Engine v2 specialization
│   └── rules-engine-agent.md # New rules, DB-driven, JSON logic, versioning
├── integrations/            # External integrations
│   └── integrations-agent.md # Webhooks, ERP/TMS, EDI, Email, S3
├── core/                    # Core infrastructure
│   ├── core-agent.md        # General backend (also here)
│   └── core-infra-agent.md  # Audit log, soft delete, middleware, rate limiting
└── ml/                      # Machine Learning
    └── ml-agent.md          # Anomaly detection, Isolation Forest, model serving
```

## Agent Responsibilities

| Agent | Specialization | Cards | Key Files |
|-------|---------------|-------|-----------|
| **core-agent** | General backend, modules, API, DB, Celery | #04, #05, #06, #12 | `app/modules/`, `app/main.py`, `prisma/schema.prisma` |
| **rules-engine-agent** | Rules Engine v2, new rules, DB-driven | #16, #17 (joint) | `app/services/rules_engine_v2.py`, `app/services/rules_critical.py` |
| **integrations-agent** | Webhooks, ERP/TMS, EDI, Email, S3 | #18 | `app/services/email_service.py`, `app/services/storage.py` |
| **core-infra-agent** | Audit log, soft delete, middleware, rate limiting | #19, #20, #04, #05 | `app/core/middleware.py`, `app/core/audit_middleware.py` |
| **ml-agent** | ML anomaly detection, model training/serving | #17 (joint) | `app/services/ml_inference.py` (new) |

## Coordination Protocol

### When to Use Which Agent

```
New feature request
        │
        ▼
┌───────────────────┐
│ What area?        │
└───────────────────┘
        │
    ┌───┼───┐
    ▼   ▼   ▼
Rules  Integ  Infra
Engine  ||   - Audit log
        ||   - Soft delete
        ▼   - Rate limit
       ML     ▼
    (Anomaly  Core
     detection) Backend
```

### Delegation Examples

```python
# New audit rule
Agent(subagent_type="rules-engine-agent", prompt="Add rule for ICMS ST on NCM 22030000")

# Webhook for ERP
Agent(subagent_type="integrations-agent", prompt="Implement webhook for discrepancy.detected event")

# Audit logging
Agent(subagent_type="core-infra-agent", prompt="Add audit log middleware for all mutations")

# ML anomaly detection
Agent(subagent_type="ml-agent", prompt="Train Isolation Forest on historical discrepancy data")

# New module (Clients)
Agent(subagent_type="core-agent", prompt="Create clients module with CRUD")
```

## Sprint 1 Priority (Current)

| Card | Agent | Title |
|------|-------|-------|
| #04 | core-infra | Rate Limiter Redis (slowapi) |
| #05 | core-infra | Rules Engine Redis Cache |
| #12 | core | XML Parser Namespace Fix |
| #06 | techlead | Deprecate NestJS |

## Sprint 2-3 Priority

| Card | Agent | Title |
|------|-------|-------|
| #18 | integrations | Webhooks for ERP/TMS |
| #19 | core-infra | Audit Log Middleware |
| #20 | core-infra | Global Soft Delete |

## Sprint 4-5 Priority (Backlog)

| Card | Agent | Title |
|------|-------|-------|
| #16 | rules-engine | Rules DB-Driven |
| #17 | ml + rules-engine | ML Anomaly Detection |

## Usage

Each agent file contains:
- Specialized context and knowledge
- Relevant cards and tasks
- Implementation patterns
- Quality gates
- Coordination protocols

Load the appropriate agent based on the task at hand.