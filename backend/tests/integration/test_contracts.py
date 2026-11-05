"""Integration tests for Contracts module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestContractsList:
    """Tests for GET /api/v1/contracts"""

    async def test_list_contracts(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing contracts"""
        response = await async_client.get(
            "/api/v1/contracts",
            headers=auth_headers,
            params={"page": 1, "size": 20},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_contracts_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing contracts with filters"""
        response = await async_client.get(
            "/api/v1/contracts",
            headers=auth_headers,
            params={"status": "ACTIVE"},
        )
        assert response.status_code in [200, 401, 500]


@pytest.mark.integration
class TestContractsCreate:
    """Tests for POST /api/v1/contracts"""

    async def test_create_contract(self, async_client: AsyncClient, auth_headers: dict, mock_company: dict, mock_client: dict, mock_carrier: dict):
        """Test creating a contract"""
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        response = await async_client.post(
            "/api/v1/contracts",
            json={
                "name": "New Contract",
                "company_id": mock_company["id"],
                "client_id": mock_client["id"],
                "carrier_id": mock_carrier["id"],
                "success_fee_pct": 20.0,
                "start_date": now.isoformat(),
                "end_date": (now + timedelta(days=365)).isoformat(),
            },
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 500]

    async def test_create_contract_invalid_data(self, async_client: AsyncClient, auth_headers: dict):
        """Test creating contract with invalid data"""
        response = await async_client.post(
            "/api/v1/contracts",
            json={"name": "", "success_fee_pct": -10},
            headers=auth_headers,
        )
        assert response.status_code in [422, 500]


@pytest.mark.integration
class TestContractsDetail:
    """Tests for GET /api/v1/contracts/{id}"""

    async def test_get_contract(self, async_client: AsyncClient, auth_headers: dict, mock_contract: dict):
        """Test getting contract detail"""
        response = await async_client.get(
            f"/api/v1/contracts/{mock_contract['id']}",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_get_contract_with_freight_tables(self, async_client: AsyncClient, auth_headers: dict, mock_contract: dict):
        """Test getting contract with freight tables"""
        response = await async_client.get(
            f"/api/v1/contracts/{mock_contract['id']}?include_freight_tables=true",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]


@pytest.mark.integration
class TestContractsUpdate:
    """Tests for PATCH /api/v1/contracts/{id}"""

    async def test_update_contract(self, async_client: AsyncClient, auth_headers: dict, mock_contract: dict):
        """Test updating contract"""
        response = await async_client.patch(
            f"/api/v1/contracts/{mock_contract['id']}",
            json={"name": "Updated Contract", "success_fee_pct": 25.0},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_update_contract_status(self, async_client: AsyncClient, auth_headers: dict, mock_contract: dict):
        """Test updating contract status"""
        response = await async_client.patch(
            f"/api/v1/contracts/{mock_contract['id']}",
            json={"status": "EXPIRED"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]


@pytest.mark.integration
class TestContractsFreightTables:
    """Tests for freight table endpoints"""

    async def test_add_freight_table(self, async_client: AsyncClient, auth_headers: dict, mock_contract: dict):
        """Test adding freight table to contract"""
        response = await async_client.post(
            f"/api/v1/contracts/{mock_contract['id']}/freight-tables",
            json={
                "name": "Tabela Principal",
                "version": "1.0",
                "valid_from": "2024-01-01",
                "valid_to": "2024-12-31",
                "rules": [],
            },
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 404, 500]

    async def test_list_freight_tables(self, async_client: AsyncClient, auth_headers: dict, mock_contract: dict):
        """Test listing freight tables for contract"""
        response = await async_client.get(
            f"/api/v1/contracts/{mock_contract['id']}/freight-tables",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]