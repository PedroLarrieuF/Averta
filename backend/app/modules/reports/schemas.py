"""Reports module schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DashboardKPIs(BaseModel):
    """Main dashboard KPIs"""

    total_recoverable: float
    total_recovered: float
    recovery_rate: float  # percentage
    total_contests: int
    active_contests: int
    conversion_rate: float  # detected -> approved
    avg_recovery_time_days: float
    top_carriers_by_volume: list[dict[str, Any]]
    top_discrepancy_types: list[dict[str, Any]]
    monthly_trend: list[dict[str, Any]]  # last 12 months


class RecoveryReportItem(BaseModel):
    """Recovery report line item"""

    contest_id: str
    contest_number: str
    client_name: str
    carrier_name: str
    contract_number: str | None
    status: str
    total_expected: float
    total_recovered: float
    success_fee_pct: float
    success_fee_value: float
    net_recovery: float
    created_at: datetime
    resolved_at: datetime | None
    # Progressive pricing info
    pricing_model: str = "FIXED"
    progressive_month: int | None = None


class RecoveryReport(BaseModel):
    """Recovery report with summary"""

    items: list[RecoveryReportItem]
    summary: dict[str, Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class SuccessFeeReportItem(BaseModel):
    """Success fee report line item"""

    contract_id: str
    contract_number: str
    carrier_name: str
    client_name: str
    success_fee_pct: float
    total_recovered: float
    success_fee_collected: float
    net_to_client: float
    contests_count: int
    # Progressive pricing info
    pricing_model: str = "FIXED"
    progressive_month1_pct: float | None = None
    progressive_month2_pct: float | None = None


class SuccessFeeReport(BaseModel):
    """Success fee report with summary"""

    items: list[SuccessFeeReportItem]
    summary: dict[str, Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class DiscrepancyStats(BaseModel):
    """Discrepancy statistics"""

    by_type: list[dict[str, Any]]
    by_status: list[dict[str, Any]]
    by_carrier: list[dict[str, Any]]
    by_client: list[dict[str, Any]]
    total_detected: int
    total_approved: int
    total_recovered: int
    total_value_detected: float
    total_value_recovered: float


class ExportRequest(BaseModel):
    """Export request parameters"""

    report_type: str = Field(..., pattern="^(recovery|success_fee|discrepancies|contests)$")
    format: str = Field(default="excel", pattern="^(excel|pdf|csv)$")
    client_id: str | None = None
    carrier_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    status: list[str] | None = None
    include_details: bool = True


class ExportResponse(BaseModel):
    """Export response"""

    file_url: str
    filename: str
    expires_at: datetime
