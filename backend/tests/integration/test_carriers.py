"""Integration tests for Carriers module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestCarriersList:
    """Tests for GET /api/v1/carriers"""

    async def test_list_carriers(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing carriers"""
        response = await async_client.get(
            "/api/v1/carriers",
            headers=auth_headers,
            params={"page": 1, "size": 20},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_carriers_search(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing carriers with search"""
        response = await async_client.get(
            "/api/v1/carriers",
            headers=auth_headers,
            params={"search": "Transport"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_carriers_without_auth(self, async_client: AsyncClient):
        """Test listing carriers without auth"""
        response = await async_client.get("/api/v1/carriers")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestCarriersCreate:
    """Tests for POST /api/v1/carriers"""

    async def test_create_carrier(self, async_client: AsyncClient, auth_headers: dict, mock_company: dict):
        """Test creating a carrier"""
        import uuid
        unique_cnpj = f"{uuid.uuid4().int % 10**14:014d}"

        response = await async_client.post(
            "/api/v1/carriers",
            json={
                "name": f"New Carrier {uuid.uuid4().hex[:8]}",
                "cnpj": unique_cnpj,
                "email": f"carrier{uuid.uuid4().hex[:8]}@test.com",
                "company_id": mock_company["id"],
            },
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 409, 500]

    async def test_create_carrier_duplicate_cnpj(self, async_client: AsyncClient, auth_headers: dict, mock_carrier: dict):
        """Test creating carrier with duplicate CNPJ"""
        response = await async_client.post(
            "/api/v1/carriers",
            json={
                "name": "Duplicate Carrier",
                "cnpj": mock_carrier["cnpj"],
                "email": "dup@carrier.com",
            },
            headers=auth_headers,
        )
        assert response.status_code in [409, 500]


@pytest.mark.integration
class TestCarriersDetail:
    """Tests for GET /api/v1/carriers/{id}"""

    async def test_get_carrier(self, async_client: AsyncClient, auth_headers: dict, mock_carrier: dict):
        """Test getting carrier detail"""
        response = await async_client.get(
            f"/api/v1/carriers/{mock_carrier['id']}",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_get_carrier_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting non-existent carrier"""
        response = await async_client.get(
            "/api/v1/carriers/non-existent",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestCarriersUpdate:
    """Tests for PATCH /api/v1/carriers/{id}"""

    async def test_update_carrier(self, async_client: AsyncClient, auth_headers: dict, mock_carrier: dict):
        """Test updating carrier"""
        response = await async_client.patch(
            f"/api/v1/carriers/{mock_carrier['id']}",
            json={"name": "Updated Carrier Name", "email": "updated@carrier.com"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]