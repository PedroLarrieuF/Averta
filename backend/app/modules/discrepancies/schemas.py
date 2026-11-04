"""Discrepancies module schemas"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class DiscrepancyStatus(StrEnum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    CONTESTED = "CONTESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"
    CLOSED = "CLOSED"


class DiscrepancySeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DiscrepancyCreate(BaseModel):
    document_id: str
    company_id: str
    rule_code: str
    rule_name: str
    discrepancy_type: str
    expected_value: float | None = None
    actual_value: float | None = None
    difference: float | None = None
    difference_pct: float | None = None
    details: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    severity: DiscrepancySeverity = DiscrepancySeverity.MEDIUM


class DiscrepancyUpdate(BaseModel):
    status: DiscrepancyStatus | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    resolution_notes: str | None = None
    contest_id: str | None = None


class DiscrepancyResponse(BaseModel):
    id: str
    document_id: str
    company_id: str
    rule_code: str
    rule_name: str
    discrepancy_type: str
    expected_value: float | None
    actual_value: float | None
    difference: float | None
    difference_pct: float | None
    details: dict[str, Any] | None
    evidence: dict[str, Any] | None
    status: str
    severity: str
    reviewed_by: str | None
    reviewed_at: datetime | None
    resolution_notes: str | None
    contest_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiscrepancyListResponse(BaseModel):
    items: list[DiscrepancyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DiscrepancySummary(BaseModel):
    total: int
    by_status: dict[str, int]
    by_severity: dict[str, int]
    by_type: dict[str, int]
    total_recoverable: float
