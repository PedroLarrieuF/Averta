"""Test data factories for integration tests"""

from tests.factories.user_factory import UserFactory
from tests.factories.company_factory import CompanyFactory
from tests.factories.client_factory import ClientFactory
from tests.factories.carrier_factory import CarrierFactory
from tests.factories.contract_factory import ContractFactory
from tests.factories.document_factory import DocumentFactory
from tests.factories.discrepancy_factory import DiscrepancyFactory

__all__ = [
    "UserFactory",
    "CompanyFactory",
    "ClientFactory",
    "CarrierFactory",
    "ContractFactory",
    "DocumentFactory",
    "DiscrepancyFactory",
]