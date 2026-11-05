"""Integration tests package"""

from tests.integration import test_auth
from tests.integration import test_documents
from tests.integration import test_discrepancies
from tests.integration import test_contests
from tests.integration import test_reports
from tests.integration import test_companies
from tests.integration import test_users
from tests.integration import test_carriers
from tests.integration import test_contracts
from tests.integration import test_notifications

__all__ = [
    "test_auth",
    "test_documents",
    "test_discrepancies",
    "test_contests",
    "test_reports",
    "test_companies",
    "test_users",
    "test_carriers",
    "test_contracts",
    "test_notifications",
]