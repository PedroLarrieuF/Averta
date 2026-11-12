"""User test data factory"""

from typing import Any


class UserFactory:
    """Factory for creating user test data"""

    _counter = 0

    @classmethod
    def _next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def build(cls, company_id: str | None = None, **overrides: Any) -> dict[str, Any]:
        """Build user data dict (without saving to DB)"""
        data = {
            "id": f"user-{cls._next_id()}",
            "email": f"user{cls._next_id()}@test.com",
            "passwordHash": "$2b$12$hashedpassword",
            "fullName": f"Test User {cls._next_id()}",
            "role": "ADMIN",
            "status": "ACTIVE",
            "companyId": company_id or "test-company-id",
            "clientId": None,
            "avatarUrl": None,
            "lastLoginAt": None,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
        data.update(overrides)
        return data

    @classmethod
    def build_with_relations(
        cls, company: dict | None = None, client: dict | None = None, **overrides: Any
    ) -> dict[str, Any]:
        """Build user data with company and client relations"""
        user = cls.build(
            company_id=company["id"] if company else None,
            client_id=client["id"] if client else None,
            **overrides,
        )
        user["company"] = company
        user["client"] = client
        return user

    @classmethod
    def build_batch(
        cls, count: int, company_id: str | None = None, **overrides: Any
    ) -> list[dict[str, Any]]:
        """Build multiple user data dicts"""
        return [cls.build(company_id=company_id, **overrides) for _ in range(count)]
