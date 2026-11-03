"""Pytest configuration with mocked dependencies for unit tests"""

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Mock Prisma before any imports
mock_prisma = MagicMock()
mock_prisma.connect = AsyncMock()
mock_prisma.disconnect = AsyncMock()

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
sys.modules["app.core.database"] = mock_db_module

# Mock app.core.config
mock_config = MagicMock()
mock_config.get_settings = MagicMock(
    return_value=MagicMock(
        JWT_SECRET_KEY="test-secret-key-for-testing-only-min-32-chars-long-here",
        JWT_REFRESH_SECRET_KEY="test-refresh-secret-key-for-testing-only-min-32-chars",
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15,
        JWT_REFRESH_TOKEN_EXPIRE_DAYS=7,
        DATABASE_URL="postgresql://postgres:postgres@localhost:5432/averta",
        REDIS_URL="redis://localhost:6379/0",
        DEBUG=True,
        ENVIRONMENT="testing",
    )
)
# Don't mock the entire app.core module - let it load normally with mocked dependencies
# sys.modules['app.core.config'] = mock_config
# sys.modules['app.core'] = MagicMock(config=mock_config, database=mock_db_module)


# Now import the actual conftest fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Async test client fixture."""
    pass


# Configure pytest-asyncio
pytest_asyncio_mode = "auto"
