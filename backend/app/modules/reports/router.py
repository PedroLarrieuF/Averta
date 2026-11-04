"""Reports module router"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CompanyIdDep,
    PaginationDep,
    RequireManager,
    get_database,
)
from app.core.rate_limit import reports_limiter
from app.modules.reports.schemas import (
    DashboardKPIs,
    DiscrepancyStats,
    ExportRequest,
    ExportResponse,
    RecoveryReport,
    SuccessFeeReport,
)
from app.modules.reports.service import ReportsService
from prisma import Prisma

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_reports_service(db: Prisma = Depends(get_database)) -> ReportsService:
    return ReportsService(db)


@router.get(
    "/dashboard",
    response_model=DashboardKPIs,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard KPIs",
)
@reports_limiter
async def get_dashboard(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    reports_service: ReportsService = Depends(get_reports_service),
) -> DashboardKPIs:
    """Get main dashboard KPIs"""
    return await reports_service.get_dashboard_kpis(company_id)


@router.get(
    "/recovery",
    response_model=RecoveryReport,
    status_code=status.HTTP_200_OK,
    summary="Get recovery report",
)
@reports_limiter
async def get_recovery_report(  # noqa: PLR0913, PLR0917
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    client_id: str | None = Query(None),
    carrier_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    status: list[str] | None = Query(None),
    reports_service: ReportsService = Depends(get_reports_service),
) -> RecoveryReport:
    """Get detailed recovery report with pagination"""
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    return await reports_service.get_recovery_report(
        company_id, pagination, client_id, carrier_id, df, dt, status
    )


@router.get(
    "/success-fee",
    response_model=SuccessFeeReport,
    status_code=status.HTTP_200_OK,
    summary="Get success fee report",
)
@reports_limiter
async def get_success_fee_report(  # noqa: PLR0913, PLR0917
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    client_id: str | None = Query(None),
    carrier_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    reports_service: ReportsService = Depends(get_reports_service),
) -> SuccessFeeReport:
    """Get success fee report grouped by contract"""
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    return await reports_service.get_success_fee_report(
        company_id, pagination, client_id, carrier_id, df, dt
    )


@router.get(
    "/discrepancies/stats",
    response_model=DiscrepancyStats,
    status_code=status.HTTP_200_OK,
    summary="Get discrepancy statistics",
)
@reports_limiter
async def get_discrepancy_stats(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    reports_service: ReportsService = Depends(get_reports_service),
) -> DiscrepancyStats:
    """Get discrepancy statistics by type, status, carrier, client"""
    return await reports_service.get_discrepancy_stats(company_id)


@router.post(
    "/export",
    response_model=ExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Export report",
)
@reports_limiter
async def export_report(
    data: ExportRequest,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    reports_service: ReportsService = Depends(get_reports_service),
) -> ExportResponse:
    """Export report to Excel (returns presigned download URL)"""
    return await reports_service.export_report(company_id, data)
