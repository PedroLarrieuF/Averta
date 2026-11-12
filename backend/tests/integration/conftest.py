"""Integration test configuration - sets up mocks before importing app"""

import asyncio
import sys
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

# ============================================================================
# Mock Prisma and Config BEFORE importing app
# ============================================================================

# Mock Prisma
mock_prisma = MagicMock()
mock_prisma.connect = AsyncMock()
mock_prisma.disconnect = AsyncMock()
mock_prisma.is_connected = MagicMock(return_value=True)

# Mock the prisma module with all submodules
prisma_mock = MagicMock(Prisma=MagicMock(return_value=mock_prisma))
prisma_mock.errors = MagicMock(PrismaError=Exception)
sys.modules["prisma"] = prisma_mock
sys.modules["prisma.client"] = MagicMock()
sys.modules["prisma.models"] = MagicMock()
sys.modules["prisma.enums"] = MagicMock()
sys.modules["prisma.errors"] = MagicMock(PrismaError=Exception)

# Mock app.core.database
mock_db_module = MagicMock()
mock_db_module.get_prisma = AsyncMock(return_value=mock_prisma)
mock_db_module.close_prisma = AsyncMock()
mock_db_module.lifespan_db = MagicMock()
mock_db_module.get_db = AsyncMock()
sys.modules["app.core.database"] = mock_db_module

# Mock app.core.config
mock_settings = MagicMock(
    JWT_SECRET_KEY="test-secret-key-for-testing-only-min-32-chars-long-here",
    JWT_REFRESH_SECRET_KEY="test-refresh-secret-key-for-testing-only-min-32-chars",
    JWT_ALGORITHM="HS256",
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS=7,
    DATABASE_URL="postgresql://postgres:postgres@localhost:5432/averta_test",
    REDIS_URL="redis://localhost:6379/0",
    DEBUG=True,
    ENVIRONMENT="testing",
    FRONTEND_URL="http://localhost:3000",
    API_PREFIX="/api/v1",
    APP_NAME="Averta SaaS",
    APP_VERSION="1.0.0",
    HOST="0.0.0.0",
    PORT=8000,
    CORS_ORIGINS=["*"],
    CORS_ALLOW_CREDENTIALS=True,
    CORS_ALLOW_METHODS=["*"],
    CORS_ALLOW_HEADERS=["*"],
    SUCCESS_FEE_PERCENTAGE=20.0,
    S3_ENDPOINT="http://localhost:9000",
    S3_ACCESS_KEY="minioadmin",
    S3_SECRET_KEY="minioadmin",
    S3_BUCKET="averta",
    SENDGRID_API_KEY="",
    SENDGRID_FROM_EMAIL="noreply@averta.com",
    SENDGRID_FROM_NAME="Averta",
)

mock_config = MagicMock()
mock_config.get_settings = MagicMock(return_value=mock_settings)
mock_config.Settings = MagicMock(return_value=mock_settings)
sys.modules["app.core.config"] = mock_config

# Mock app.core.security (for token creation)

mock_security = MagicMock()
# create_tokens returns a mock with access_token and refresh_token
mock_tokens = MagicMock()
mock_tokens.access_token = "mock-access-token"
mock_tokens.refresh_token = "mock-refresh-token"
mock_tokens.expires_in = 900
mock_security.create_tokens = MagicMock(return_value=mock_tokens)
mock_security.create_password_reset_token = MagicMock(return_value="mock-reset-token")
mock_security.decode_access_token = MagicMock(
    return_value=MagicMock(
        sub="test-user-id",
        email="test@test.com",
        role="ADMIN",
        company_id="test-company-id",
        client_id=None,
    )
)
mock_security.decode_refresh_token = MagicMock(
    return_value=MagicMock(
        sub="test-user-id",
    )
)
mock_security.verify_password_reset_token = MagicMock(return_value="test@test.com")
mock_security.get_password_hash = MagicMock(return_value="$2b$12$hashedpassword")
mock_security.verify_password = MagicMock(return_value=True)
sys.modules["app.core.security"] = mock_security

# Mock app.core.exceptions
mock_exceptions = MagicMock()
mock_exceptions.AppException = Exception
mock_exceptions.UnauthorizedError = Exception
mock_exceptions.ForbiddenError = Exception
mock_exceptions.NotFoundError = Exception
mock_exceptions.BadRequestError = Exception
mock_exceptions.ConflictError = Exception
mock_exceptions.ValidationError = Exception
sys.modules["app.core.exceptions"] = mock_exceptions

# Mock app.core.middleware
mock_middleware = MagicMock()
mock_middleware.LoggingMiddleware = MagicMock()
mock_middleware.RequestIDMiddleware = MagicMock()
mock_middleware.SecurityHeadersMiddleware = MagicMock()
mock_middleware.StructlogMiddleware = MagicMock()
sys.modules["app.core.middleware"] = mock_middleware

# Mock app.core.rate_limit
mock_rate_limit = MagicMock()
mock_rate_limit.init_rate_limiter = MagicMock()
mock_rate_limit.rate_limit_exceeded_handler = MagicMock()
mock_rate_limit.auth_limiter = MagicMock()
sys.modules["app.core.rate_limit"] = mock_rate_limit

# Mock app.core.dependencies
mock_dependencies = MagicMock()
mock_dependencies.get_database = AsyncMock(return_value=mock_prisma)
mock_dependencies.CurrentUserDep = MagicMock()
mock_dependencies.CompanyIdDep = MagicMock()
mock_dependencies.ClientIdDep = MagicMock()
mock_dependencies.PaginationDep = MagicMock()
mock_dependencies.FilterDep = MagicMock()
mock_dependencies.SortDep = MagicMock()
mock_dependencies.RateLimitDep = MagicMock()
mock_dependencies.RequestIdDep = MagicMock()
sys.modules["app.core.dependencies"] = mock_dependencies

# Mock slowapi
slowapi_mock = MagicMock()
slowapi_mock.errors = MagicMock(RateLimitExceeded=Exception)
slowapi_mock.Limiter = MagicMock()
slowapi_mock._rate_limit_exceeded_handler = MagicMock()
sys.modules["slowapi"] = slowapi_mock
sys.modules["slowapi.errors"] = MagicMock(RateLimitExceeded=Exception)

# Mock prisma.errors
prisma_errors_mock = MagicMock(PrismaError=Exception)
sys.modules["prisma.errors"] = prisma_errors_mock

# Mock jose
jose_mock = MagicMock()
jose_mock.JWTError = Exception
jose_mock.jwt = MagicMock()
sys.modules["jose"] = jose_mock
sys.modules["jose.jwt"] = MagicMock()

# Now import the app
from app.main import app

# Configure pytest-asyncio
pytest_asyncio_mode = "auto"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Integration Test Fixtures
# ============================================================================


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client for API testing against the FastAPI app."""
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
        data = {
            "name": f"Test Company {cls._next_id()}",
            "cnpj": f"{cls._next_id():014d}",
            "email": f"company{cls._next_id()}@test.com",
        }
        data.update(overrides)
        return data

    @classmethod
    def user_data(cls, company_id: str | None = None, **overrides) -> dict:
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
    def contract_data(
        cls,
        company_id: str | None = None,
        client_id: str | None = None,
        carrier_id: str | None = None,
        **overrides,
    ) -> dict:
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
    def document_data(
        cls, company_id: str | None = None, client_id: str | None = None, **overrides
    ) -> dict:
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
    def discrepancy_data(
        cls, document_id: str | None = None, contract_id: str | None = None, **overrides
    ) -> dict:
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
    def contest_data(
        cls, company_id: str | None = None, client_id: str | None = None, **overrides
    ) -> dict:
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
    return TestDataFactory()


# ============================================================================
# Auth Fixtures (Mock)
# ============================================================================


@pytest.fixture
async def test_company(async_client: AsyncClient, test_factory: TestDataFactory) -> dict:
    company_data = test_factory.company_data()
    company_data["id"] = "test-company-id"
    return company_data


@pytest.fixture
async def test_user(
    async_client: AsyncClient, test_company: dict, test_factory: TestDataFactory
) -> dict:
    user_data = test_factory.user_data(company_id=test_company["id"])
    user_data["id"] = "test-user-id"
    return user_data


@pytest.fixture
async def auth_headers(async_client: AsyncClient, test_user: dict) -> dict:
    return {"Authorization": "Bearer mock-access-token"}


@pytest.fixture
async def admin_auth_headers(async_client: AsyncClient, test_company: dict) -> dict:
    return {"Authorization": "Bearer mock-access-token"}


# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def mock_company() -> dict:
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
    import os

    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
    os.environ["CELERY_TASK_EAGER_PROPAGATES"] = "true"
    yield
    if "CELERY_TASK_ALWAYS_EAGER" in os.environ:
        del os.environ["CELERY_TASK_ALWAYS_EAGER"]
    if "CELERY_TASK_EAGER_PROPAGATES" in os.environ:
        del os.environ["CELERY_TASK_EAGER_PROPAGATES"]


# ============================================================================
# Redis Test Fixture (using fakeredis)
# ============================================================================


@pytest.fixture
async def redis_client():
    try:
        import fakeredis.aioredis

        redis = fakeredis.aioredis.FakeRedis()
        yield redis
        await redis.close()
    except ImportError:
        yield MagicMock()


# ============================================================================
# MinIO Test Fixture (mock)
# ============================================================================


@pytest.fixture
def minio_client():
    return MagicMock()


# ============================================================================
# SendGrid Test Fixture (mock)
# ============================================================================


@pytest.fixture
def sendgrid_client():
    return MagicMock()
