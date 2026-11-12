"""Integration tests package"""

from tests.integration import (
    test_auth,
    test_carriers,
    test_companies,
    test_contests,
    test_contracts,
    test_discrepancies,
    test_documents,
    test_notifications,
    test_reports,
    test_users,
)

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
