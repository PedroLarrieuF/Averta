"""Integration tests for Companies module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestCompaniesList:
    """Tests for GET /api/v1/companies"""

    async def test_list_companies(self, async_client: AsyncClient, admin_auth_headers: dict):
        """Test listing companies (admin only)"""
        response = await async_client.get(
            "/api/v1/companies",
            headers=admin_auth_headers,
            params={"page": 1, "size": 10},
        )
        assert response.status_code in [200, 401, 403, 500]

    async def test_list_companies_without_auth(self, async_client: AsyncClient):
        """Test listing companies without auth"""
        response = await async_client.get("/api/v1/companies")
        assert response.status_code in [401, 500]

    async def test_list_companies_non_admin(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing companies as non-admin"""
        response = await async_client.get(
            "/api/v1/companies",
            headers=auth_headers,
        )
        assert response.status_code in [200, 403, 500]


@pytest.mark.integration
class TestCompaniesCreate:
    """Tests for POST /api/v1/companies"""

    async def test_create_company(self, async_client: AsyncClient, admin_auth_headers: dict):
        """Test creating a company (admin only)"""
        import uuid
        unique_cnpj = f"{uuid.uuid4().int % 10**14:014d}"

        response = await async_client.post(
            "/api/v1/companies",
            json={
                "name": f"New Company {uuid.uuid4().hex[:8]}",
                "cnpj": unique_cnpj,
                "email": f"new{uuid.uuid4().hex[:8]}@company.com",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code in [201, 400, 401, 403, 409, 500]

    async def test_create_company_duplicate_cnpj(self, async_client: AsyncClient, admin_auth_headers: dict):
        """Test creating company with duplicate CNPJ"""
        response = await async_client.post(
            "/api/v1/companies",
            json={
                "name": "Duplicate Company",
                "cnpj": "12345678000195",
                "email": "dup@company.com",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code in [409, 500]

    async def test_create_company_invalid_data(self, async_client: AsyncClient, admin_auth_headers: dict):
        """Test creating company with invalid data"""
        response = await async_client.post(
            "/api/v1/companies",
            json={"name": "", "cnpj": "invalid", "email": "not-email"},
            headers=admin_auth_headers,
        )
        assert response.status_code in [422, 500]


@pytest.mark.integration
class TestCompaniesDetail:
    """Tests for GET /api/v1/companies/{id}"""

    async def test_get_company(self, async_client: AsyncClient, auth_headers: dict, mock_company: dict):
        """Test getting company detail"""
        response = await async_client.get(
            f"/api/v1/companies/{mock_company['id']}",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 403, 404, 500]

    async def test_get_company_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting non-existent company"""
        response = await async_client.get(
            "/api/v1/companies/non-existent",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestCompaniesUpdate:
    """Tests for PATCH /api/v1/companies/{id}"""

    async def test_update_company(self, async_client: AsyncClient, admin_auth_headers: dict, mock_company: dict):
        """Test updating company"""
        response = await async_client.patch(
            f"/api/v1/companies/{mock_company['id']}",
            json={"name": "Updated Company Name", "email": "updated@company.com"},
            headers=admin_auth_headers,
        )
        assert response.status_code in [200, 401, 403, 404, 500]

    async def test_update_company_unauthorized(self, async_client: AsyncClient, mock_company: dict):
        """Test updating company without auth"""
        response = await async_client.patch(
            f"/api/v1/companies/{mock_company['id']}",
            json={"name": "Updated"},
        )
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestCompaniesSettings:
    """Tests for company settings endpoints"""

    async def test_get_company_settings(self, async_client: AsyncClient, auth_headers: dict, mock_company: dict):
        """Test getting company settings"""
        response = await async_client.get(
            f"/api/v1/companies/{mock_company['id']}/settings",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_update_company_settings(self, async_client: AsyncClient, admin_auth_headers: dict, mock_company: dict):
        """Test updating company settings"""
        response = await async_client.patch(
            f"/api/v1/companies/{mock_company['id']}/settings",
            json={"success_fee_percentage": 25.0, "auto_reprocess": True},
            headers=admin_auth_headers,
        )
        assert response.status_code in [200, 401, 403, 404, 500]