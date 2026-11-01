"""Discrepancies module"""
from app.modules.discrepancies.router import router
from app.modules.discrepancies.service import DiscrepanciesService
from app.modules.discrepancies.schemas import (
    DiscrepancyCreate,
    DiscrepancyUpdate,
    DiscrepancyResponse,
    DiscrepancyListResponse,
    DiscrepancyStatus,
    DiscrepancySeverity,
)

__all__ = [
    "router",
    "DiscrepanciesService",
    "DiscrepancyCreate",
    "DiscrepancyUpdate",
    "DiscrepancyResponse",
    "DiscrepancyListResponse",
    "DiscrepancyStatus",
    "DiscrepancySeverity",
]