---
id: 29
title: "Backend Integration Tests (httpx.AsyncClient)"
priority: high
type: feature
agent: backend
sprint: 1
estimate: L
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #29: Backend Integration Tests (httpx.AsyncClient)

## Description
Implement comprehensive integration tests for all API endpoints using `httpx.AsyncClient` against a test database. This addresses TD-005 (Integration Tests) and TD-010 (some test failures).

## Acceptance Criteria

### Test Infrastructure
- [ ] Test database setup (separate test DB or transaction rollback)
- [ ] `conftest.py` fixtures: `async_client`, `test_db`, `auth_headers`, `test_company`, `test_user`
- [ ] Test data factories using `factory_boy` or similar
- [ ] Redis test instance (fakeredis or testcontainers)

### Authentication Module Tests
- [ ] `POST /auth/login` - valid credentials, invalid credentials, inactive user
- [ ] `POST /auth/register` - valid data, duplicate email, invalid data
- [ ] `POST /auth/refresh` - valid refresh token, expired token, revoked token
- [ ] `POST /auth/logout` - revokes refresh token
- [ ] `GET /auth/me` - with valid token, without token, with expired token
- [ ] `POST /auth/forgot-password` / `POST /auth/reset-password`

### Documents Module Tests
- [ ] `POST /documents/upload` - valid XML, invalid XML, duplicate, unauthorized
- [ ] `GET /documents` - pagination, filters (status, type, date), search
- [ ] `GET /documents/{id}` - exists, not found, unauthorized
- [ ] `POST /documents/{id}/reprocess` - triggers reprocessing

### Discrepancies Module Tests
- [ ] `GET /discrepancies` - pagination, filters (status, severity, rule, date), search
- [ ] `GET /discrepancies/summary` - returns KPIs by status/severity/rule
- [ ] `PATCH /discrepancies/bulk-status` - valid IDs, invalid IDs, unauthorized
- [ ] `POST /discrepancies/{id}/review` - marks as reviewed

### Contests Module Tests
- [ ] `POST /contests` - create from discrepancies, validation
- [ ] `GET /contests` - pagination, filters, search
- [ ] `GET /contests/{id}` - details with items and communications
- [ ] `POST /contests/{id}/send` - generates PDF, sends email
- [ ] `PATCH /contests/{id}/negotiate` - status transitions
- [ ] `POST /contests/{id}/payments` - register payment

### Reports Module Tests
- [ ] `GET /reports/dashboard` - KPIs, time series, top carriers/rules
- [ ] `GET /reports/pdf` - returns PDF binary
- [ ] `GET /reports/excel` - returns Excel binary
- [ ] `POST /reports/schedule` - create scheduled report

### Settings Modules Tests (Companies, Users, Carriers, Contracts)
- [ ] CRUD operations for each
- [ ] Permission checks (role-based access)
- [ ] Validation tests

### Notifications Module Tests
- [ ] `GET /notifications` - pagination, filters
- [ ] `PATCH /notifications/{id}/read` - mark as read
- [ ] `GET /notifications/preferences` / `PATCH /notifications/preferences`

## Technical Requirements

### Test Structure
```
backend/tests/
├── conftest.py                 # Fixtures (enhance existing)
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
└── test_rules_critical.py      # Existing unit tests
```

### Key Fixtures (conftest.py)
```python
@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_db():
    """Test database with transaction rollback."""
    # Use test DATABASE_URL or transaction rollback
    pass

@pytest.fixture
def auth_headers(test_user, test_company):
    """Authenticated headers for API calls."""
    # Login and return Authorization header
    pass

@pytest.fixture
def test_company(test_db):
    """Create test company."""
    pass

@pytest.fixture
def test_user(test_company, test_db):
    """Create test user."""
    pass
```

### Test Patterns
```python
# Example integration test
async def test_login_success(async_client, test_user):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

# Example with auth
async def test_get_documents_list(async_client, auth_headers, test_document):
    response = await async_client.get(
        "/api/v1/documents",
        headers=auth_headers,
        params={"page": 1, "size": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
```

## Dependencies
- Card #28: Fix Failing Rule Tests (should be done first)
- Card #04, #05: Redis infrastructure (DONE)
- Backend: All API endpoints implemented

## Testing Requirements
- Target: ≥80% coverage for new integration tests
- Run in CI pipeline
- Use pytest markers: `@pytest.mark.integration`
- Mock external services: MinIO (fakeredis), SendGrid (mock), Celery (eager mode)

## CI Configuration
```yaml
# .github/workflows/ci-cd.yml - add integration test job
- name: Run integration tests
  run: |
    cd backend
    poetry run pytest -m "integration" -v --cov=app --cov-report=xml
```

## Definition of Done
- [ ] All integration test modules created
- [ ] All API endpoints covered with happy path + error cases
- [ ] Tests run in CI and pass
- [ ] Coverage ≥80% for integration tests
- [ ] Full test suite passes: `poetry run test-cov`
- [ ] Card moved to `review/`

## Notes
- This is a LARGE card - consider breaking into sub-cards per module
- Use `httpx.AsyncClient` with `ASGITransport` for fast in-process testing
- Test database: use separate test DB or SQLite in-memory for speed
- Celery: set `task_always_eager=True` in test config
- Redis: use `fakeredis` for testing
- MinIO: mock or use testcontainer
- SendGrid: mock email service