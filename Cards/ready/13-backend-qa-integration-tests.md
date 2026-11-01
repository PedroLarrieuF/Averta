---
id: 13
title: "Add Backend Integration Tests (httpx.AsyncClient)"
priority: high
type: tech-debt
agent: backend-qa
sprint: 2
estimate: L
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 13: Add Backend Integration Tests

## Contexto
Backend tem ~78% coverage mas **faltam testes de integração** para rotas autenticadas (TD-005). Apenas testes unitários de rules.

## Definition of Ready
- [x] pytest + httpx + pytest-asyncio configurados
- [x] conftest.py com fixtures (db, client, auth tokens)
- [x] 50+ testes de rules em `test_rules_critical.py`

## Tasks
- [ ] Criar fixtures de integração em `tests/conftest.py`:
  - `async_client` - httpx.AsyncClient com ASGITransport
  - `auth_headers` - tokens válidos para cada role
  - `test_company`, `test_client`, `test_carrier`, `test_contract`
  - `test_document`, `test_discrepancy`, `test_contest`
- [ ] Testes Auth:
  - `test_login_success`, `test_login_invalid`, `test_refresh_token`, `test_logout`
  - `test_register_company_user`
- [ ] Testes Documents:
  - `test_upload_cte_xml`, `test_upload_invalid_xml`, `test_list_documents`, `test_reprocess`
- [ ] Testes Discrepancies:
  - `test_list_with_filters`, `test_summary`, `test_bulk_status`, `test_review`
- [ ] Testes Contests:
  - `test_create_from_discrepancies`, `test_send_generates_pdf`, `test_negotiate`, `test_payment`
- [ ] Testes Reports:
  - `test_dashboard`, `test_pdf_export`, `test_excel_export`
- [ ] Configurar banco de teste separado (transaction rollback por teste)
- [ ] CI: rodar integration tests em stage separado

## Test Structure
```python
# tests/integration/test_auth.py
async def test_login_success(async_client, test_user):
    response = await async_client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

# tests/integration/test_documents.py
async def test_upload_cte_xml(async_client, auth_headers, sample_cte_xml):
    files = {"file": ("test.xml", sample_cte_xml, "application/xml")}
    response = await async_client.post("/api/v1/documents/upload", files=files, headers=auth_headers)
    assert response.status_code == 201
```

## Acceptance Criteria
- [ ] Integração tests cobrem todos endpoints principais
- [ ] Rodam isolados (transaction rollback)
- [ ] CI passa com integration tests
- [ ] Coverage sobe para >85%
- [ ] Docs: como rodar localmente

## Referências
- `TECHLEAD_REVIEW.md` - TD-005
- `backend/pyproject.toml` - pytest config
- `backend/tests/conftest.py` - fixtures atuais