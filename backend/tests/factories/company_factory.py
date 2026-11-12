"""Company test data factory"""

from typing import Any


class CompanyFactory:
    """Factory for creating company test data"""

    _counter = 0

    @classmethod
    def _next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def build(cls, **overrides: Any) -> dict[str, Any]:
        """Build company data dict (without saving to DB)"""
        data = {
            "id": f"company-{cls._next_id()}",
            "name": f"Test Company {cls._next_id()}",
            "cnpj": f"{cls._next_id():014d}",
            "email": f"company{cls._next_id()}@test.com",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
        data.update(overrides)
        return data

    @classmethod
    def build_batch(cls, count: int, **overrides: Any) -> list[dict[str, Any]]:
        """Build multiple company data dicts"""
        return [cls.build(**overrides) for _ in range(count)]
