# ADR-001: Python FastAPI as Primary Backend

**Date:** 2026-11-02  
**Status:** Accepted  
**Deciders:** Tech Lead (AvertaSaaS)  
**Technical Story:** Card #06 - Decision: Deprecate NestJS Backend

## Context

The AvertaSaaS project contains **two backend implementations**:

1. **`backend/`** - Python FastAPI + Prisma + Celery + PostgreSQL + Redis
   - ✅ Complete implementation (11 modules, 17 audit rules)
   - ✅ Comprehensive documentation (`backend/README.md`)
   - ✅ Test coverage ~78% (50+ rule tests)
   - ✅ Production-ready: Clean Architecture, RBAC, multi-tenancy, async throughout
   - ✅ CI/CD pipeline configured (lint, typecheck, test, build, deploy)
   - ✅ Docker Compose for local dev + production
   - ✅ Rules Engine v2 with tag-based O(tag) filtering
   - ✅ Document processing pipeline (XML → parse → rules → discrepancies)
   - ✅ Contest workflow with PDF generation, success-fee calculation

2. **`packages/backend/`** - NestJS + Prisma + BullMQ
   - 🟡 Partial/duplicate implementation
   - 🟡 No comprehensive documentation
   - 🟡 No test coverage visible
   - 🟡 Separate infra (different Docker, different ports)
   - 🟡 Creates confusion for team onboarding

## Decision

**Deprecate and archive the NestJS backend (`packages/backend/`).** Python FastAPI (`backend/`) is the single source of truth for backend development.

## Rationale

| Factor | Python FastAPI | NestJS |
|--------|---------------|--------|
| **Completion** | 100% (all 17 rules, full audit pipeline) | Partial |
| **Documentation** | Comprehensive README (source of truth) | Minimal |
| **Testing** | 78% coverage, 50+ rule tests | Unknown/none |
| **Rules Engine** | v2 with smart tag filtering | Not implemented |
| **Domain Fit** | Python excels at data processing, ML, rules | TypeScript parity only |
| **Team Context** | Backend agents specialized for Python | No dedicated NestJS agents |
| **Future Roadmap** | ML anomaly detection, rules DB-driven | Would require reimplementation |

The Python backend is **production-ready** and aligns with the project's domain (freight audit = heavy data processing, tax rules, ML). Maintaining two backends doubles maintenance burden, creates onboarding confusion, and splits team focus.

## Consequences

### Positive
- Single backend focus → faster feature delivery
- Reduced maintenance burden (one CI/CD, one infra, one test suite)
- Clear onboarding path for new developers
- Python ecosystem advantages for rules engine, ML, data processing

### Negative
- Sunk cost in NestJS implementation (mitigated: archive for reference)
- TypeScript end-to-end not achieved (frontend remains TS, backend is Python)

### Neutral
- OpenAPI spec → TypeScript types generation still viable (planned)
- Frontend unaffected (proxies `/api` → `localhost:8000`)

## Implementation Plan

1. ✅ **Document decision** in this ADR
2. 🔄 **Archive `packages/backend/`** → move to `archived/packages-backend-nestjs/`
3. 🔄 **Update root `package.json`** - remove `@averta/backend` workspace reference
4. 🔄 **Update `turbo.json`** - remove NestJS pipeline
5. 🔄 **Communicate** to team in `#averta-tech`
6. 🔄 **Update onboarding docs** (CLAUDE.md, agent files)

## Alternatives Considered

| Option | Verdict |
|--------|---------|
| Maintain both backends | Rejected: duplication, confusion, 2x maintenance |
| Migrate to NestJS | Rejected: would require rewriting 17 rules, tests, infra, Rules Engine v2 |
| Keep NestJS as "reference" | Accepted: archive folder preserves code for reference |

## Related

- **TD-008** in `TECHLEAD_REVIEW.md` - NestJS backend duplicate
- **ADR-009** in `techlead-agent.md` - Python FastAPI is Primary Backend (already documented)
- Card #06 - This decision card

---

**Supersedes:** None  
**Superseded by:** None