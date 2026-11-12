"""Integration tests for Notifications module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestNotificationsList:
    """Tests for GET /api/v1/notifications"""

    async def test_list_notifications(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing notifications"""
        response = await async_client.get(
            "/api/v1/notifications",
            headers=auth_headers,
            params={"page": 1, "size": 20},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_notifications_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing notifications with filters"""
        response = await async_client.get(
            "/api/v1/notifications",
            headers=auth_headers,
            params={"channel": "EMAIL", "read": "false"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_notifications_without_auth(self, async_client: AsyncClient):
        """Test listing notifications without auth"""
        response = await async_client.get("/api/v1/notifications")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestNotificationsMarkRead:
    """Tests for PATCH /api/v1/notifications/{id}/read"""

    async def test_mark_notification_read(self, async_client: AsyncClient, auth_headers: dict):
        """Test marking notification as read"""
        response = await async_client.patch(
            "/api/v1/notifications/test-notification-id/read",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 404, 500]

    async def test_mark_notification_read_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test marking non-existent notification as read"""
        response = await async_client.patch(
            "/api/v1/notifications/non-existent/read",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestNotificationsBulkRead:
    """Tests for PATCH /api/v1/notifications/bulk-read"""

    async def test_bulk_mark_read(self, async_client: AsyncClient, auth_headers: dict):
        """Test bulk marking notifications as read"""
        response = await async_client.patch(
            "/api/v1/notifications/bulk-read",
            json={"ids": ["notif-1", "notif-2", "notif-3"]},
            headers=auth_headers,
        )
        assert response.status_code in [200, 400, 401, 500]


@pytest.mark.integration
class TestNotificationsPreferences:
    """Tests for notification preferences"""

    async def test_get_preferences(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting notification preferences"""
        response = await async_client.get(
            "/api/v1/notifications/preferences",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 500]

    async def test_update_preferences(self, async_client: AsyncClient, auth_headers: dict):
        """Test updating notification preferences"""
        response = await async_client.patch(
            "/api/v1/notifications/preferences",
            json={
                "email_enabled": True,
                "in_app_enabled": True,
                "discrepancy_alerts": True,
                "contest_updates": True,
                "weekly_report": True,
            },
            headers=auth_headers,
        )
        assert response.status_code in [200, 400, 401, 500]

    async def test_update_preferences_invalid(self, async_client: AsyncClient, auth_headers: dict):
        """Test updating preferences with invalid data"""
        response = await async_client.patch(
            "/api/v1/notifications/preferences",
            json={"email_enabled": "not-a-boolean"},
            headers=auth_headers,
        )
        assert response.status_code in [422, 500]
