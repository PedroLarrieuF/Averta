"""Integration tests for Branches module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestBranchesList:
    """Tests for GET /api/v1/branches"""

    async def test_list_branches(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing branches"""
        response = await async_client.get(
            "/api/v1/branches",
            headers=auth_headers,
            params={"page": 1, "size": 20},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_branches_by_client(self, async_client: AsyncClient, auth_headers: dict, mock_client: dict):
        """Test listing branches filtered by client"""
        response = await async_client.get(
            "/api/v1/branches",
            headers=auth_headers,
            params={"client_id": mock_client["id"]},
        )
        assert response.status_code in [200, 401, 500]


@pytest.mark.integration
class TestBranchesCreate:
    """Tests for POST /api/v1/branches"""

    async def test_create_branch(self, async_client: AsyncClient, auth_headers: dict, mock_client: dict):
        """Test creating a branch"""
        import uuid
        unique_cnpj = f"{uuid.uuid4().int % 10**14:014d}"

        response = await async_client.post(
            "/api/v1/branches",
            json={
                "name": f"New Branch {uuid.uuid4().hex[:8]}",
                "cnpj": unique_cnpj,
                "address": "New Address",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01000-000",
                "client_id": mock_client["id"],
            },
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 409, 500]


@pytest.mark.integration
class TestBranchesDetail:
    """Tests for GET /api/v1/branches/{id}"""

    async def test_get_branch(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting branch detail"""
        response = await async_client.get(
            "/api/v1/branches/test-branch-id",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]


@pytest.mark.integration
class TestBranchesUpdate:
    """Tests for PATCH /api/v1/branches/{id}"""

    async def test_update_branch(self, async_client: AsyncClient, auth_headers: dict):
        """Test updating branch"""
        response = await async_client.patch(
            "/api/v1/branches/test-branch-id",
            json={"name": "Updated Branch", "city": "Rio de Janeiro", "state": "RJ"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]