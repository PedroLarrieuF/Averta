"""Pytest configuration with integration test fixtures using httpx.AsyncClient"""

import asyncio
import sys
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Configure pytest-asyncio
pytest_asyncio_mode = "auto"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Integration Test Fixtures (using httpx.AsyncClient with ASGITransport)
# ============================================================================

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client for API testing against the FastAPI app.

    This fixture creates a test client with mocked dependencies.
    """
    # Import app here to ensure mocks are in place
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ============================================================================
# Test Data Factories
# ============================================================================

class TestDataFactory:
    """Factory for creating test data"""

    _counter = 0

    @classmethod
    def _next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def company_data(cls, **overrides) -> dict:
        """Generate company test data"""
        data = {
            "name": f"Test Company {cls._next_id()}",
            "cnpj": f"{cls._next_id():014d}",
            "email": f"company{cls._next_id()}@test.com",
        }
        data.update(overrides)
        return data

    @classmethod
    def user_data(cls, company_id: str | None = None, **overrides) -> dict:
        """Generate user test data"""
        data = {
            "email": f"user{cls._next_id()}@test.com",
            "passwordHash": "$2b$12$hashedpassword",
            "fullName": f"Test User {cls._next_id()}",
            "role": "ADMIN",
            "status": "ACTIVE",
            "companyId": company_id or "test-company-id",
        }
        data.update(overrides)
        return data

    @classmethod
    def client_data(cls, company_id: str | None = None, **overrides) -> dict:
        """Generate client test data"""
        data = {
            "name": f"Test Client {cls._next_id()}",
            "cnpj": f"{cls._next_id():014d}",
            "email": f"client{cls._next_id()}@test.com",
            "companyId": company_id or "test-company-id",
        }
        data.update(overrides)
        return data

    @classmethod
    def carrier_data(cls, company_id: str | None = None, **overrides) -> dict:
        """Generate carrier test data"""
        data = {
            "name": f"Test Carrier {cls._next_id()}",
            "cnpj": f"{cls._next_id():014d}",
            "email": f"carrier{cls._next_id()}@test.com",
            "companyId": company_id or "test-company-id",
        }
        data.update(overrides)
        return data

    @classmethod
    def branch_data(cls, client_id: str | None = None, **overrides) -> dict:
        """Generate branch test data"""
        data = {
            "name": f"Test Branch {cls._next_id()}",
            "cnpj": f"{cls._next_id():014d}",
            "address": "Test Address",
            "city": "São Paulo",
            "state": "SP",
            "zipCode": "01000-000",
            "clientId": client_id or "test-client-id",
        }
        data.update(overrides)
        return data

    @classmethod
    def contract_data(cls, company_id: str | None = None, client_id: str | None = None, carrier_id: str | None = None, **overrides) -> dict:
        """Generate contract test data"""
        from datetime import UTC, datetime, timedelta

        data = {
            "name": f"Test Contract {cls._next_id()}",
            "companyId": company_id or "test-company-id",
            "clientId": client_id or "test-client-id",
            "carrierId": carrier_id or "test-carrier-id",
            "successFeePct": 20.0,
            "startDate": datetime.now(UTC),
            "endDate": datetime.now(UTC) + timedelta(days=365),
            "status": "ACTIVE",
        }
        data.update(overrides)
        return data

    @classmethod
    def document_data(cls, company_id: str | None = None, client_id: str | None = None, **overrides) -> dict:
        """Generate document test data"""
        data = {
            "fileName": f"test_document_{cls._next_id()}.xml",
            "fileSize": 1024,
            "type": "CTE",
            "status": "PENDING",
            "companyId": company_id or "test-company-id",
            "clientId": client_id,
        }
        data.update(overrides)
        return data

    @classmethod
    def discrepancy_data(cls, document_id: str | None = None, contract_id: str | None = None, **overrides) -> dict:
        """Generate discrepancy test data"""
        data = {
            "type": "ICMS_DIFFERENTIAL",
            "ruleCode": "ICMS_DIFAL",
            "severity": "HIGH",
            "status": "OPEN",
            "expectedValue": 1000.0,
            "actualValue": 1100.0,
            "difference": 100.0,
            "differencePct": 10.0,
            "documentId": document_id or "test-doc-id",
            "contractId": contract_id or "test-contract-id",
        }
        data.update(overrides)
        return data

    @classmethod
    def contest_data(cls, company_id: str | None = None, client_id: str | None = None, **overrides) -> dict:
        """Generate contest test data"""
        data = {
            "number": f"CTST-{cls._next_id():06d}",
            "status": "DRAFT",
            "companyId": company_id or "test-company-id",
            "clientId": client_id or "test-client-id",
            "carrierId": "test-carrier-id",
            "successFeePct": 20.0,
            "totalContested": 1000.0,
            "successFeeValue": 200.0,
            "netRecovery": 800.0,
        }
        data.update(overrides)
        return data


@pytest.fixture
def test_factory() -> TestDataFactory:
    """Test data factory fixture"""
    return TestDataFactory


# ============================================================================
# Auth Fixtures (Mock - for testing endpoint behavior without real DB)
# ============================================================================

@pytest.fixture
async def test_company(async_client: AsyncClient, test_factory: TestDataFactory) -> dict:
    """Create a test company via API (or return mock data)"""
    company_data = test_factory.company_data()
    company_data["id"] = "test-company-id"
    return company_data


@pytest.fixture
async def test_user(async_client: AsyncClient, test_company: dict, test_factory: TestDataFactory) -> dict:
    """Create a test user"""
    user_data = test_factory.user_data(company_id=test_company["id"])
    user_data["id"] = "test-user-id"
    return user_data


@pytest.fixture
async def auth_headers(async_client: AsyncClient, test_user: dict) -> dict:
    """Get authentication headers by creating a mock token"""
    from app.core.security import create_tokens

    tokens = create_tokens(
        subject=test_user["id"],
        email=test_user["email"],
        role=test_user["role"],
        company_id=test_user["companyId"],
        client_id=test_user.get("clientId"),
    )
    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest.fixture
async def admin_auth_headers(async_client: AsyncClient, test_company: dict) -> dict:
    """Get admin authentication headers"""
    from app.core.security import create_tokens

    tokens = create_tokens(
        subject="admin-user-id",
        email="admin@test.com",
        role="ADMIN",
        company_id=test_company["id"],
    )
    return {"Authorization": f"Bearer {tokens.access_token}"}


# ============================================================================
# Mock Data Fixtures (for tests that don't need real DB)
# ============================================================================

@pytest.fixture
def mock_company() -> dict:
    """Mock company data"""
    return {
        "id": "test-company-id",
        "name": "Test Company",
        "cnpj": "12345678000195",
        "email": "company@test.com",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_user(mock_company: dict) -> dict:
    """Mock user data"""
    return {
        "id": "test-user-id",
        "email": "user@test.com",
        "fullName": "Test User",
        "role": "ADMIN",
        "status": "ACTIVE",
        "companyId": mock_company["id"],
        "clientId": None,
        "avatarUrl": None,
        "lastLoginAt": None,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "company": mock_company,
        "client": None,
    }


@pytest.fixture
def mock_client(mock_company: dict) -> dict:
    """Mock client data"""
    return {
        "id": "test-client-id",
        "name": "Test Client",
        "cnpj": "12345678000195",
        "email": "client@test.com",
        "companyId": mock_company["id"],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_carrier(mock_company: dict) -> dict:
    """Mock carrier data"""
    return {
        "id": "test-carrier-id",
        "name": "Test Carrier",
        "cnpj": "98765432000123",
        "email": "carrier@test.com",
        "companyId": mock_company["id"],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_contract(mock_company: dict, mock_client: dict, mock_carrier: dict) -> dict:
    """Mock contract data"""
    return {
        "id": "test-contract-id",
        "name": "Test Contract",
        "companyId": mock_company["id"],
        "clientId": mock_client["id"],
        "carrierId": mock_carrier["id"],
        "successFeePct": 20.0,
        "startDate": "2024-01-01T00:00:00Z",
        "endDate": "2025-01-01T00:00:00Z",
        "status": "ACTIVE",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_document(mock_company: dict, mock_client: dict) -> dict:
    """Mock document data"""
    return {
        "id": "test-doc-id",
        "fileName": "test.xml",
        "fileSize": 1024,
        "type": "CTE",
        "status": "COMPLETED",
        "companyId": mock_company["id"],
        "clientId": mock_client["id"],
        "contractId": "test-contract-id",
        "parsedData": {},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_discrepancy(mock_document: dict, mock_contract: dict) -> dict:
    """Mock discrepancy data"""
    return {
        "id": "test-discrepancy-id",
        "type": "ICMS_DIFFERENTIAL",
        "ruleCode": "ICMS_DIFAL",
        "severity": "HIGH",
        "status": "OPEN",
        "expectedValue": 1000.0,
        "actualValue": 1100.0,
        "difference": 100.0,
        "differencePct": 10.0,
        "documentId": mock_document["id"],
        "contractId": mock_contract["id"],
        "metadata": {},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
    }


# ============================================================================
# Celery Test Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def celery_eager_mode():
    """Set Celery to eager mode for testing"""
    import os
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
    os.environ["CELERY_TASK_EAGER_PROPAGATES"] = "true"
    yield
    # Cleanup
    if "CELERY_TASK_ALWAYS_EAGER" in os.environ:
        del os.environ["CELERY_TASK_ALWAYS_EAGER"]
    if "CELERY_TASK_EAGER_PROPAGATES" in os.environ:
        del os.environ["CELERY_TASK_EAGER_PROPAGATES"]


# ============================================================================
# Redis Test Fixture (using fakeredis)
# ============================================================================

@pytest.fixture
async def redis_client():
    """Fake Redis client for testing"""
    try:
        import fakeredis.aioredis
        redis = fakeredis.aioredis.FakeRedis()
        yield redis
        await redis.close()
    except ImportError:
        # Fallback to mock if fakeredis not available
        yield MagicMock()


# ============================================================================
# MinIO Test Fixture (mock)
# ============================================================================

@pytest.fixture
def minio_client():
    """Mock MinIO client for testing"""
    return MagicMock()


# ============================================================================
# SendGrid Test Fixture (mock)
# ============================================================================

@pytest.fixture
def sendgrid_client():
    """Mock SendGrid client for testing"""
    return MagicMock()