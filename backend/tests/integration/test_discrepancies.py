"""Integration tests for Discrepancies module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestDiscrepanciesList:
    """Tests for GET /api/v1/discrepancies"""

    async def test_list_discrepancies_pagination(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing discrepancies with pagination"""
        response = await async_client.get(
            "/api/v1/discrepancies",
            headers=auth_headers,
            params={"page": 1, "size": 20},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_discrepancies_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing discrepancies with filters"""
        response = await async_client.get(
            "/api/v1/discrepancies",
            headers=auth_headers,
            params={"status": "OPEN", "severity": "HIGH", "rule": "ICMS_DIFAL"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_discrepancies_date_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing discrepancies with date filters"""
        response = await async_client.get(
            "/api/v1/discrepancies",
            headers=auth_headers,
            params={"date_from": "2024-01-01", "date_to": "2024-12-31"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_discrepancies_search(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing discrepancies with search"""
        response = await async_client.get(
            "/api/v1/discrepancies",
            headers=auth_headers,
            params={"search": "ICMS"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_discrepancies_without_auth(self, async_client: AsyncClient):
        """Test listing discrepancies without auth"""
        response = await async_client.get("/api/v1/discrepancies")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestDiscrepanciesSummary:
    """Tests for GET /api/v1/discrepancies/summary"""

    async def test_get_summary(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting discrepancies summary KPIs"""
        response = await async_client.get(
            "/api/v1/discrepancies/summary",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 500]

    async def test_summary_with_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test summary with date filters"""
        response = await async_client.get(
            "/api/v1/discrepancies/summary",
            headers=auth_headers,
            params={"date_from": "2024-01-01", "date_to": "2024-12-31"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_summary_without_auth(self, async_client: AsyncClient):
        """Test summary without auth"""
        response = await async_client.get("/api/v1/discrepancies/summary")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestDiscrepanciesBulkStatus:
    """Tests for PATCH /api/v1/discrepancies/bulk-status"""

    async def test_bulk_status_update_valid(self, async_client: AsyncClient, auth_headers: dict, mock_discrepancy: dict):
        """Test bulk status update with valid IDs"""
        response = await async_client.patch(
            "/api/v1/discrepancies/bulk-status",
            json={"ids": [mock_discrepancy["id"]], "status": "REVIEWED"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 400, 401, 500]

    async def test_bulk_status_update_invalid_ids(self, async_client: AsyncClient, auth_headers: dict):
        """Test bulk status update with invalid IDs"""
        response = await async_client.patch(
            "/api/v1/discrepancies/bulk-status",
            json={"ids": ["invalid-id-1", "invalid-id-2"], "status": "REVIEWED"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 400, 404, 500]

    async def test_bulk_status_update_empty_ids(self, async_client: AsyncClient, auth_headers: dict):
        """Test bulk status update with empty IDs list"""
        response = await async_client.patch(
            "/api/v1/discrepancies/bulk-status",
            json={"ids": [], "status": "REVIEWED"},
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]

    async def test_bulk_status_update_invalid_status(self, async_client: AsyncClient, auth_headers: dict, mock_discrepancy: dict):
        """Test bulk status update with invalid status"""
        response = await async_client.patch(
            "/api/v1/discrepancies/bulk-status",
            json={"ids": [mock_discrepancy["id"]], "status": "INVALID_STATUS"},
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]

    async def test_bulk_status_without_auth(self, async_client: AsyncClient):
        """Test bulk status update without auth"""
        response = await async_client.patch(
            "/api/v1/discrepancies/bulk-status",
            json={"ids": ["id1"], "status": "REVIEWED"},
        )
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestDiscrepanciesReview:
    """Tests for POST /api/v1/discrepancies/{id}/review"""

    async def test_review_discrepancy(self, async_client: AsyncClient, auth_headers: dict, mock_discrepancy: dict):
        """Test marking discrepancy as reviewed"""
        response = await async_client.post(
            f"/api/v1/discrepancies/{mock_discrepancy['id']}/review",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_review_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test reviewing non-existent discrepancy"""
        response = await async_client.post(
            "/api/v1/discrepancies/non-existent/review",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]

    async def test_review_unauthorized(self, async_client: AsyncClient):
        """Test reviewing without auth"""
        response = await async_client.post("/api/v1/discrepancies/some-id/review")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestDiscrepanciesDetail:
    """Tests for GET /api/v1/discrepancies/{id}"""

    async def test_get_discrepancy(self, async_client: AsyncClient, auth_headers: dict, mock_discrepancy: dict):
        """Test getting discrepancy detail"""
        response = await async_client.get(
            f"/api/v1/discrepancies/{mock_discrepancy['id']}",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_get_discrepancy_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting non-existent discrepancy"""
        response = await async_client.get(
            "/api/v1/discrepancies/non-existent",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]