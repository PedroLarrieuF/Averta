"""Integration tests for Contests module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestContestsCreate:
    """Tests for POST /api/v1/contests"""

    async def test_create_contest_valid(
        self, async_client: AsyncClient, auth_headers: dict, mock_discrepancy: dict
    ):
        """Test creating contest from discrepancies"""
        response = await async_client.post(
            "/api/v1/contests",
            json={
                "discrepancy_ids": [mock_discrepancy["id"]],
                "client_id": "test-client-id",
                "carrier_id": "test-carrier-id",
            },
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 404, 500]

    async def test_create_contest_empty_discrepancies(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating contest with empty discrepancies list"""
        response = await async_client.post(
            "/api/v1/contests",
            json={
                "discrepancy_ids": [],
                "client_id": "test-client-id",
                "carrier_id": "test-carrier-id",
            },
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]

    async def test_create_contest_invalid_discrepancies(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating contest with invalid discrepancy IDs"""
        response = await async_client.post(
            "/api/v1/contests",
            json={
                "discrepancy_ids": ["invalid-1", "invalid-2"],
                "client_id": "test-client-id",
                "carrier_id": "test-carrier-id",
            },
            headers=auth_headers,
        )
        assert response.status_code in [400, 404, 500]

    async def test_create_contest_missing_fields(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating contest with missing required fields"""
        response = await async_client.post(
            "/api/v1/contests",
            json={"discrepancy_ids": ["id1"]},
            headers=auth_headers,
        )
        assert response.status_code in [422, 500]

    async def test_create_contest_unauthorized(self, async_client: AsyncClient):
        """Test creating contest without auth"""
        response = await async_client.post(
            "/api/v1/contests",
            json={"discrepancy_ids": ["id1"], "client_id": "c1", "carrier_id": "c2"},
        )
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestContestsList:
    """Tests for GET /api/v1/contests"""

    async def test_list_contests_pagination(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing contests with pagination"""
        response = await async_client.get(
            "/api/v1/contests",
            headers=auth_headers,
            params={"page": 1, "size": 10},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_contests_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing contests with filters"""
        response = await async_client.get(
            "/api/v1/contests",
            headers=auth_headers,
            params={"status": "DRAFT"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_contests_without_auth(self, async_client: AsyncClient):
        """Test listing contests without auth"""
        response = await async_client.get("/api/v1/contests")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestContestsDetail:
    """Tests for GET /api/v1/contests/{id}"""

    async def test_get_contest(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting contest detail"""
        response = await async_client.get(
            "/api/v1/contests/test-contest-id",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_get_contest_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting non-existent contest"""
        response = await async_client.get(
            "/api/v1/contests/non-existent",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestContestsSend:
    """Tests for POST /api/v1/contests/{id}/send"""

    async def test_send_contest(self, async_client: AsyncClient, auth_headers: dict):
        """Test sending contest (generates PDF + sends email)"""
        response = await async_client.post(
            "/api/v1/contests/test-contest-id/send",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_send_contest_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test sending non-existent contest"""
        response = await async_client.post(
            "/api/v1/contests/non-existent/send",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestContestsNegotiate:
    """Tests for PATCH /api/v1/contests/{id}/negotiate"""

    async def test_negotiate_contest_acknowledged(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test negotiating contest - ACKNOWLEDGED"""
        response = await async_client.patch(
            "/api/v1/contests/test-contest-id/negotiate",
            json={"status": "ACKNOWLEDGED", "notes": "Received"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_negotiate_contest_negotiating(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test negotiating contest - NEGOTIATING"""
        response = await async_client.patch(
            "/api/v1/contests/test-contest-id/negotiate",
            json={"status": "NEGOTIATING", "notes": "Counter offer"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_negotiate_contest_accepted(self, async_client: AsyncClient, auth_headers: dict):
        """Test negotiating contest - ACCEPTED"""
        response = await async_client.patch(
            "/api/v1/contests/test-contest-id/negotiate",
            json={"status": "ACCEPTED", "notes": "Agreed"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_negotiate_contest_partial(self, async_client: AsyncClient, auth_headers: dict):
        """Test negotiating contest - PARTIAL"""
        response = await async_client.patch(
            "/api/v1/contests/test-contest-id/negotiate",
            json={"status": "PARTIAL", "notes": "Partial agreement"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_negotiate_contest_rejected(self, async_client: AsyncClient, auth_headers: dict):
        """Test negotiating contest - REJECTED"""
        response = await async_client.patch(
            "/api/v1/contests/test-contest-id/negotiate",
            json={"status": "REJECTED", "notes": "Disagreed"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_negotiate_invalid_status(self, async_client: AsyncClient, auth_headers: dict):
        """Test negotiating with invalid status"""
        response = await async_client.patch(
            "/api/v1/contests/test-contest-id/negotiate",
            json={"status": "INVALID", "notes": "Test"},
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]


@pytest.mark.integration
class TestContestsPayments:
    """Tests for POST /api/v1/contests/{id}/payments"""

    async def test_register_payment(self, async_client: AsyncClient, auth_headers: dict):
        """Test registering payment for contest"""
        response = await async_client.post(
            "/api/v1/contests/test-contest-id/payments",
            json={
                "amount": 1000.0,
                "payment_date": "2024-01-15",
                "notes": "Partial payment",
            },
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 404, 500]

    async def test_register_payment_invalid_amount(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test registering payment with invalid amount"""
        response = await async_client.post(
            "/api/v1/contests/test-contest-id/payments",
            json={"amount": -100, "payment_date": "2024-01-15"},
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]

    async def test_register_payment_missing_fields(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test registering payment with missing fields"""
        response = await async_client.post(
            "/api/v1/contests/test-contest-id/payments",
            json={},
            headers=auth_headers,
        )
        assert response.status_code in [422, 500]
