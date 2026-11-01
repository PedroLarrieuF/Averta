"""Discrepancies module schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DiscrepancyStatus(str, Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    CONTESTED = "CONTESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"
    CLOSED = "CLOSED"


class DiscrepancySeverity(str, Enum):
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
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    difference: Optional[float] = None
    difference_pct: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    evidence: Optional[Dict[str, Any]] = None
    severity: DiscrepancySeverity = DiscrepancySeverity.MEDIUM


class DiscrepancyUpdate(BaseModel):
    status: Optional[DiscrepancyStatus] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    contest_id: Optional[str] = None


class DiscrepancyResponse(BaseModel):
    id: str
    document_id: str
    company_id: str
    rule_code: str
    rule_name: str
    discrepancy_type: str
    expected_value: Optional[float]
    actual_value: Optional[float]
    difference: Optional[float]
    difference_pct: Optional[float]
    details: Optional[Dict[str, Any]]
    evidence: Optional[Dict[str, Any]]
    status: str
    severity: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    resolution_notes: Optional[str]
    contest_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiscrepancyListResponse(BaseModel):
    items: List[DiscrepancyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DiscrepancySummary(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_severity: Dict[str, int]
    by_type: Dict[str, int]
    total_recoverable: float