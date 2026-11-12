"""Discrepancy test data factory"""

from typing import Any


class DiscrepancyFactory:
    """Factory for creating discrepancy test data"""

    _counter = 0

    @classmethod
    def _next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def build(
        cls,
        document_id: str | None = None,
        contract_id: str | None = None,
        **overrides: Any,
    ) -> dict[str, Any]:
        """Build discrepancy data dict (without saving to DB)"""
        data = {
            "id": f"disc-{cls._next_id()}",
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
            "metadata": {},
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
        data.update(overrides)
        return data

    @classmethod
    def build_batch(
        cls,
        count: int,
        document_id: str | None = None,
        contract_id: str | None = None,
        **overrides: Any,
    ) -> list[dict[str, Any]]:
        """Build multiple discrepancy data dicts"""
        return [
            cls.build(document_id=document_id, contract_id=contract_id, **overrides)
            for _ in range(count)
        ]
