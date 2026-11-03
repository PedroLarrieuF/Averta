"""Discrepancies module"""

from app.modules.discrepancies.router import router
from app.modules.discrepancies.schemas import (
    DiscrepancyCreate,
    DiscrepancyListResponse,
    DiscrepancyResponse,
    DiscrepancySeverity,
    DiscrepancyStatus,
    DiscrepancyUpdate,
)
from app.modules.discrepancies.service import DiscrepanciesService

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
