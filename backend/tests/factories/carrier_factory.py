"""Carrier test data factory"""

from typing import Any


class CarrierFactory:
    """Factory for creating carrier test data"""

    _counter = 0

    @classmethod
    def _next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def build(cls, company_id: str | None = None, **overrides: Any) -> dict[str, Any]:
        """Build carrier data dict (without saving to DB)"""
        data = {
            "id": f"carrier-{cls._next_id()}",
            "name": f"Test Carrier {cls._next_id()}",
            "cnpj": f"{cls._next_id():014d}",
            "email": f"carrier{cls._next_id()}@test.com",
            "companyId": company_id or "test-company-id",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
        data.update(overrides)
        return data

    @classmethod
    def build_batch(cls, count: int, company_id: str | None = None, **overrides: Any) -> list[dict[str, Any]]:
        """Build multiple carrier data dicts"""
        return [cls.build(company_id=company_id, **overrides) for _ in range(count)]