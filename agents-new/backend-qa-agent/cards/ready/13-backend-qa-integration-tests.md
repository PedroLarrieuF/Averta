---
id: 13
title: "Integration Tests (httpx.AsyncClient)"
priority: medium
type: feature
agent: backend-qa
sprint: 1
estimate: L
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #13: Integration Tests (httpx.AsyncClient) - QA Perspective

## Description
Implement comprehensive integration tests for all API endpoints using `httpx.AsyncClient` against a test database. This is the QA agent's version of Card #29 (backend-agent) - focused on test quality, coverage, and validation.

## Acceptance Criteria

### Test Infrastructure (QA Standards)
- [ ] Test database: isolated test DB with migrations
- [ ] Fixtures: reusable, well-documented, parameterized
- [ ] Test data factories: realistic, varied, edge cases covered
- [ ] External service mocks: MinIO (fakeredis), SendGrid (mock), Celery (eager)
- [ ] CI integration: runs on every PR, blocks merge on failure

### Test Quality Requirements
- [ ] Each endpoint: happy path + 3+ error cases
- [ ] Authentication/Authorization: test all role combinations
- [ ] Multi-tenancy: verify company_id isolation
- [ ] Data integrity: verify DB state after each operation
- [ ] Performance: basic latency assertions (<500ms for simple GETs)

### Coverage Targets
- [ ] Integration test coverage: ≥80% of API routes
- [ ] Critical paths: 100% (auth, document processing, contest workflow)
- [ ] Edge cases: documented and tested

### Test Organization
```
backend/tests/
├── conftest.py                 # Shared fixtures (enhance)
├── factories/                  # Test data factories
│   ├── __init__.py
│   ├── user_factory.py
│   ├── company_factory.py
│   ├── client_factory.py
│   ├── carrier_factory.py
│   ├── contract_factory.py
│   ├── document_factory.py
│   └── discrepancy_factory.py
├── integration/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_documents.py
│   ├── test_discrepancies.py
│   ├── test_contests.py
│   ├── test_reports.py
│   ├── test_companies.py
│   ├── test_users.py
│   ├── test_carriers.py
│   ├── test_contracts.py
│   └── test_notifications.py
├── contract/                   # API contract tests
│   ├── __init__.py
│   └── test_openapi_spec.py    # Validate responses match OpenAPI
└── test_rules_critical.py      # Existing unit tests
```

### Specific Test Scenarios (QA Focus)

#### Auth Security Tests
- [ ] Brute force protection (rate limiting on login)
- [ ] JWT token expiration and refresh flow
- [ ] Password reset token expiration
- [ ] Role-based access control on all endpoints

#### Document Processing Tests
- [ ] Valid CT-e XML → parsed + discrepancies created
- [ ] Valid NF-e XML → parsed + discrepancies created
- [ ] Invalid XML → proper error response
- [ ] Duplicate document detection
- [ ] Reprocess triggers re-evaluation

#### Discrepancy Workflow Tests
- [ ] List with all filter combinations
- [ ] Bulk status update with partial failures
- [ ] Review action audit trail
- [ ] Summary accuracy verification

#### Contest Workflow Tests
- [ ] Create contest from discrepancies
- [ ] Send contest → PDF generated + email queued
- [ ] Negotiate status transitions (valid/invalid)
- [ ] Payment registration → fee calculation + notifications

#### Multi-tenancy Tests
- [ ] Company A cannot see Company B's data
- [ ] Cross-company API calls return 403/404
- [ ] User with CLIENT role sees only their client_id data

## Technical Requirements

### Test Configuration
```python
# pytest.ini or pyproject.toml additions
[pytest]
markers =
    integration: Integration tests requiring database
    contract: API contract validation tests
    security: Security-focused tests
    slow: Tests taking >5s

# Test database
DATABASE_URL_TEST=postgresql://postgres:postgres@localhost:5432/averta_test
REDIS_URL_TEST=redis://localhost:6379/1
```

### CI Pipeline Integration
```yaml
# .github/workflows/ci-cd.yml
- name: Start test services
  run: docker-compose -f docker-compose.test.yml up -d

- name: Run integration tests
  run: |
    cd backend
    DATABASE_URL=$DATABASE_URL_TEST poetry run pytest -m "integration" -v --cov=app --cov-report=xml

- name: Run contract tests
  run: |
    cd backend
    poetry run pytest -m "contract" -v

- name: Run security tests
  run: |
    cd backend
    poetry run pytest -m "security" -v
```

## Dependencies
- Card #28: Fix Failing Rule Tests (prerequisite)
- Card #04, #05: Redis infrastructure (DONE)
- Backend-agent Card #29: Same scope, implementation perspective

## Coordination
- **Backend Agent** implements the test infrastructure and factories
- **Backend QA Agent** defines test scenarios, validates coverage, ensures quality
- **Tech Lead** reviews test strategy and approves coverage targets

## Definition of Done
- [ ] All integration test modules created with QA-grade scenarios
- [ ] Test factories cover all domain entities with realistic data
- [ ] Security tests validate auth/z and multi-tenancy
- [ ] Contract tests validate OpenAPI compliance
- [ ] CI pipeline runs integration tests on every PR
- [ ] Coverage targets met and reported
- [ ] Card moved to `review/`

## Notes
- This card complements backend-agent Card #29
- QA agent focuses on WHAT to test and quality standards
- Backend agent focuses on HOW to implement the test infrastructure
- Both agents should coordinate on test design
- Consider using `pytest-xdist` for parallel test execution
- Use `testcontainers` for Redis/Postgres in CI if needed