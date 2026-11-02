---
id: 32
title: "Sprint Planning - New Cards Prioritization"
priority: high
type: decision
agent: po-scrum
sprint: 1
estimate: S
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #32: Sprint Planning - New Cards Prioritization

## Description
Prioritize and assign the 12 new cards created during the documentation update to appropriate sprints and agents.

## New Cards Summary

| Card | Agent | Title | Estimate | Priority | Suggested Sprint |
|------|-------|-------|----------|----------|------------------|
| #21 | frontend | Reports Page | L | HIGH | Sprint 2 |
| #22 | frontend | Clients Page | M | HIGH | Sprint 2 |
| #23 | frontend | Carriers Page | M | HIGH | Sprint 2 |
| #24 | frontend | Contracts Page | L | HIGH | Sprint 2 |
| #25 | frontend | Profile Page | S | MEDIUM | Sprint 2 |
| #26 | frontend | Code Splitting | M | MEDIUM | Sprint 3 |
| #27 | frontend | TypeScript Types | S | LOW | Sprint 3 |
| #28 | backend | Fix Failing Rule Tests | M | HIGH | Sprint 1 |
| #29 | backend | Integration Tests | L | HIGH | Sprint 1 |
| #30 | backend | Rate Limit Import Fix | S | HIGH | Sprint 1 |
| #13 | backend-qa | Integration Tests (QA) | L | MEDIUM | Sprint 1 |
| #31 | techlead | Documentation Update | S | HIGH | Sprint 1 (DONE) |

## Sprint 1 (Current - Immediate)
**Goal**: Fix critical backend issues + start integration tests

| Card | Agent | Action |
|------|-------|--------|
| #28 | backend | Fix 6 failing rule tests (BLOCKER for quality gate) |
| #30 | backend | Fix rate limit import (quick win) |
| #29 | backend | Start integration test infrastructure |
| #13 | backend-qa | Define QA test scenarios, review test design |
| #31 | techlead | DONE - Documentation updated |

**Capacity**: Backend (1 dev) + Backend QA (1 dev) + Tech Lead (part-time)

## Sprint 2 (Next - Frontend Focus)
**Goal**: Complete core user-facing pages (7 pages)

| Card | Agent | Estimate | Dependencies |
|------|-------|----------|--------------|
| #10 | frontend | XL | Contests Page (was in ready) |
| #21 | frontend | L | Reports Page |
| #22 | frontend | M | Clients Page |
| #23 | frontend | M | Carriers Page |
| #24 | frontend | L | Contracts Page (most complex) |
| #25 | frontend | S | Profile Page |
| #03 | frontend | M | Dashboard Charts (was in ready) |
| #07 | frontend | L | Design System Enhancements (was in ready) |

**Capacity**: Frontend (1-2 devs) - Consider parallelizing Clients/Carriers/Profile

**Total Sprint 2 Estimate**: ~XL + L + M + M + L + S + M + L = ~70-80 story points

## Sprint 3 (Technical Debt)
**Goal**: Performance + Type Safety

| Card | Agent | Estimate |
|------|-------|----------|
| #26 | frontend | M | Code Splitting (995kB → <500kB) |
| #27 | frontend | S | TypeScript Types Barrel Exports |
| #16 | backend | L | Rules DB-Driven Configuration |
| #17 | backend | XL | ML Anomaly Detection |
| #18 | backend | L | Webhooks System |
| #19 | backend | M | Audit Log Middleware |
| #20 | backend | M | Soft Delete Global |

## Coordination Notes

### Frontend Parallelization Strategy (Sprint 2)
- **Dev 1**: Contests Page (#10) - XL, longest
- **Dev 2**: Reports (#21) + Clients (#22) + Carriers (#23) - Can share patterns
- **Dev 3** (if available): Contracts (#24) + Profile (#25) + Dashboard (#03)

### Shared Components (Create Once, Use Many)
- `ClientForm` / `CarrierForm` - Very similar, create shared base
- `BranchForm` / `BranchesTable` - Shared across Clients/Carriers
- `CRUDTable` - Generic table with pagination, sorting, filters
- `CRUDModal` - Generic create/edit modal

### Backend Prerequisites for Sprint 2
- All API endpoints must be working (they are per backend/README.md)
- Integration tests (#29, #13) should cover endpoints before frontend consumes
- Fix failing rule tests (#28) to ensure discrepancy data is accurate

## Definition of Done
- [ ] Sprint 1 cards assigned and in progress
- [ ] Sprint 2 cards prioritized and in `ready/` for frontend-agent
- [ ] Sprint 3 cards remain in `backlog/` for now
- [ ] Dependencies between cards documented
- [ ] Capacity planning confirmed with team
- [ ] Card moved to `review/`

## Notes
- This is a planning card for PO/Scrum agent
- Actual sprint assignments happen when agents pick up cards
- Frontend Sprint 2 is the biggest - may need 2 sprints
- Backend Sprint 1 is critical for unblocking quality gates