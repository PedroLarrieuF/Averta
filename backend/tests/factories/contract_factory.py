"""Contract test data factory"""

from datetime import UTC, datetime, timedelta
from typing import Any


class ContractFactory:
    """Factory for creating contract test data"""

    _counter = 0

    @classmethod
    def _next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def build(
        cls,
        company_id: str | None = None,
        client_id: str | None = None,
        carrier_id: str | None = None,
        **overrides: Any,
    ) -> dict[str, Any]:
        """Build contract data dict (without saving to DB)"""
        now = datetime.now(UTC)
        data = {
            "id": f"contract-{cls._next_id()}",
            "name": f"Test Contract {cls._next_id()}",
            "companyId": company_id or "test-company-id",
            "clientId": client_id or "test-client-id",
            "carrierId": carrier_id or "test-carrier-id",
            "successFeePct": 20.0,
            "startDate": now.isoformat(),
            "endDate": (now + timedelta(days=365)).isoformat(),
            "status": "ACTIVE",
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat(),
        }
        data.update(overrides)
        return data

    @classmethod
    def build_batch(
        cls,
        count: int,
        company_id: str | None = None,
        client_id: str | None = None,
        carrier_id: str | None = None,
        **overrides: Any,
    ) -> list[dict[str, Any]]:
        """Build multiple contract data dicts"""
        return [
            cls.build(
                company_id=company_id, client_id=client_id, carrier_id=carrier_id, **overrides
            )
            for _ in range(count)
        ]
