"""Document test data factory"""

from typing import Any


class DocumentFactory:
    """Factory for creating document test data"""

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
        contract_id: str | None = None,
        **overrides: Any,
    ) -> dict[str, Any]:
        """Build document data dict (without saving to DB)"""
        data = {
            "id": f"doc-{cls._next_id()}",
            "fileName": f"test_document_{cls._next_id()}.xml",
            "fileSize": 1024,
            "type": "CTE",
            "status": "PENDING",
            "companyId": company_id or "test-company-id",
            "clientId": client_id,
            "contractId": contract_id,
            "parsedData": {},
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
        data.update(overrides)
        return data

    @classmethod
    def build_batch(
        cls,
        count: int,
        company_id: str | None = None,
        client_id: str | None = None,
        contract_id: str | None = None,
        **overrides: Any,
    ) -> list[dict[str, Any]]:
        """Build multiple document data dicts"""
        return [
            cls.build(company_id=company_id, client_id=client_id, contract_id=contract_id, **overrides)
            for _ in range(count)
        ]