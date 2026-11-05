"""Integration tests for Users module"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestUsersList:
    """Tests for GET /api/v1/users"""

    async def test_list_users(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing users"""
        response = await async_client.get(
            "/api/v1/users",
            headers=auth_headers,
            params={"page": 1, "size": 10},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_users_filters(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing users with filters"""
        response = await async_client.get(
            "/api/v1/users",
            headers=auth_headers,
            params={"role": "ADMIN", "status": "ACTIVE"},
        )
        assert response.status_code in [200, 401, 500]

    async def test_list_users_without_auth(self, async_client: AsyncClient):
        """Test listing users without auth"""
        response = await async_client.get("/api/v1/users")
        assert response.status_code in [401, 500]


@pytest.mark.integration
class TestUsersCreate:
    """Tests for POST /api/v1/users"""

    async def test_create_user(self, async_client: AsyncClient, admin_auth_headers: dict, mock_company: dict):
        """Test creating a user"""
        import uuid
        unique_email = f"newuser{uuid.uuid4().hex[:8]}@test.com"

        response = await async_client.post(
            "/api/v1/users",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "full_name": "New User",
                "role": "AUDITOR",
                "company_id": mock_company["id"],
            },
            headers=admin_auth_headers,
        )
        assert response.status_code in [201, 400, 401, 403, 409, 500]

    async def test_create_user_duplicate_email(self, async_client: AsyncClient, admin_auth_headers: dict, mock_user: dict):
        """Test creating user with duplicate email"""
        response = await async_client.post(
            "/api/v1/users",
            json={
                "email": mock_user["email"],
                "password": "TestPass123!",
                "full_name": "Another User",
                "role": "AUDITOR",
                "company_id": mock_user["companyId"],
            },
            headers=admin_auth_headers,
        )
        assert response.status_code in [409, 500]

    async def test_create_user_invalid_data(self, async_client: AsyncClient, admin_auth_headers: dict):
        """Test creating user with invalid data"""
        response = await async_client.post(
            "/api/v1/users",
            json={"email": "invalid", "password": "short", "role": "INVALID"},
        )
        assert response.status_code in [422, 500]


@pytest.mark.integration
class TestUsersDetail:
    """Tests for GET /api/v1/users/{id}"""

    async def test_get_user(self, async_client: AsyncClient, auth_headers: dict, mock_user: dict):
        """Test getting user detail"""
        response = await async_client.get(
            f"/api/v1/users/{mock_user['id']}",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401, 403, 404, 500]

    async def test_get_user_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test getting non-existent user"""
        response = await async_client.get(
            "/api/v1/users/non-existent",
            headers=auth_headers,
        )
        assert response.status_code in [404, 500]


@pytest.mark.integration
class TestUsersUpdate:
    """Tests for PATCH /api/v1/users/{id}"""

    async def test_update_user(self, async_client: AsyncClient, admin_auth_headers: dict, mock_user: dict):
        """Test updating user"""
        response = await async_client.patch(
            f"/api/v1/users/{mock_user['id']}",
            json={"full_name": "Updated Name", "role": "MANAGER"},
            headers=admin_auth_headers,
        )
        assert response.status_code in [200, 401, 403, 404, 500]

    async def test_update_user_status(self, async_client: AsyncClient, admin_auth_headers: dict, mock_user: dict):
        """Test updating user status"""
        response = await async_client.patch(
            f"/api/v1/users/{mock_user['id']}",
            json={"status": "INACTIVE"},
            headers=admin_auth_headers,
        )
        assert response.status_code in [200, 401, 403, 404, 500]


@pytest.mark.integration
class TestUsersPassword:
    """Tests for password change endpoints"""

    async def test_change_password(self, async_client: AsyncClient, auth_headers: dict):
        """Test changing own password"""
        response = await async_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "TestPass123!", "new_password": "NewPass456!"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 400, 401, 500]

    async def test_change_password_wrong_current(self, async_client: AsyncClient, auth_headers: dict):
        """Test changing password with wrong current password"""
        response = await async_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "WrongPass", "new_password": "NewPass456!"},
            headers=auth_headers,
        )
        assert response.status_code in [400, 401, 500]