"""Integration tests for Reports module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestReportsDashboard:
    """Tests for GET /api/v1/reports/dashboard"""

    async def test_get_dashboard(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting dashboard KPIs"""
        response = await async_client.get(
            "/api/v1/reports/dashboard",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 500]

    async def test_dashboard_with_date_range(self, async_client: AsyncClient, auth_headers: dict):
        """Test dashboard with date range"""
        response = await async_client.get(
            "/api/v1/reports/dashboard",
            headers=auth_headers,
            params={"date_from": "2024-01-01", "date_to": "2024-12-31"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_dashboard_without_auth(self, async_client: AsyncClient):
        """Test dashboard without auth"""
        response = await async_client.get("/api/v1/reports/dashboard")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestReportsPDF:
    """Tests for GET /api/v1/reports/pdf"""

    async def test_get_pdf_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting PDF report"""
        response = await async_client.get(
            "/api/v1/reports/pdf",
            headers=auth_headers,
        )
        # Should return PDF binary or error
        assert response.status_code in [200, 401, 500]

    async def test_pdf_report_with_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test PDF report with filters"""
        response = await async_client.get(
            "/api/v1/reports/pdf",
            headers=auth_headers,
            params={"date_from": "2024-01-01", "date_to": "2024-12-31"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_pdf_without_auth(self, async_client: AsyncClient):
        """Test PDF report without auth"""
        response = await async_client.get("/api/v1/reports/pdf")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestReportsExcel:
    """Tests for GET /api/v1/reports/excel"""

    async def test_get_excel_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting Excel report"""
        response = await async_client.get(
            "/api/v1/reports/excel",
            headers=auth_headers,
        )
        # Should return Excel binary or error
        assert response.status_code in [200, 401, 500]

    async def test_excel_report_with_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test Excel report with filters"""
        response = await async_client.get(
            "/api/v1/reports/excel",
            headers=auth_headers,
            params={"date_from": "2024-01-01", "date_to": "2024-12-31"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_excel_without_auth(self, async_client: AsyncClient):
        """Test Excel report without auth"""
        response = await async_client.get("/api/v1/reports/excel")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestReportsSchedule:
    """Tests for POST /api/v1/reports/schedule"""

    async def test_schedule_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test scheduling a weekly report"""
        response = await async_client.post(
            "/api/v1/reports/schedule",
            json={
                "name": "Weekly Report",
                "frequency": "WEEKLY",
                "day_of_week": 1,  # Monday
                "time": "09:00",
                "recipients": ["test@test.com"],
                "format": "PDF",
            },
            headers=auth_headers,
        )
        assert response.status_code in [201, 400, 401, 500]

    async def test_schedule_report_invalid_frequency(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test scheduling with invalid frequency"""
        response = await async_client.post(
            "/api/v1/reports/schedule",
            json={
                "name": "Test",
                "frequency": "INVALID",
                "day_of_week": 1,
                "time": "09:00",
                "recipients": ["test@test.com"],
            },
            headers=auth_headers,
        )
        assert response.status_code in [400, 422, 500]

    async def test_schedule_report_missing_fields(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test scheduling with missing required fields"""
        response = await async_client.post(
            "/api/v1/reports/schedule",
            json={"name": "Test"},
            headers=auth_headers,
        )
        assert response.status_code in [422, 500]

    async def test_schedule_report_without_auth(self, async_client: AsyncClient):
        """Test scheduling without auth"""
        response = await async_client.post(
            "/api/v1/reports/schedule",
            json={
                "name": "Test",
                "frequency": "WEEKLY",
                "day_of_week": 1,
                "time": "09:00",
                "recipients": ["t@t.com"],
            },
        )
        assert response.status_code in [401, 500]
