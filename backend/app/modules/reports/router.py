"""Reports module router"""
from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from datetime import datetime
from prisma import Prisma

from app.core.dependencies import (
    get_database,
    CurrentUserDep,
    RequireManager,
    RequireAdmin,
    CompanyIdDep,
    PaginationDep,
)
from app.modules.reports.schemas import (
    DashboardKPIs,
    RecoveryReport,
    SuccessFeeReport,
    DiscrepancyStats,
    ExportRequest,
    ExportResponse,
)
from app.modules.reports.service import ReportsService

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_reports_service(db: Prisma = Depends(get_database)) -> ReportsService:
    return ReportsService(db)


@router.get(
    "/dashboard",
    response_model=DashboardKPIs,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard KPIs",
)
async def get_dashboard(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    reports_service: ReportsService = Depends(get_reports_service),
):
    """Get main dashboard KPIs"""
    return await reports_service.get_dashboard_kpis(company_id)


@router.get(
    "/recovery",
    response_model=RecoveryReport,
    status_code=status.HTTP_200_OK,
    summary="Get recovery report",
)
async def get_recovery_report(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    client_id: str | None = Query(None),
    carrier_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    status: List[str] | None = Query(None),
    reports_service: ReportsService = Depends(get_reports_service),
):
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
async def get_success_fee_report(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    client_id: str | None = Query(None),
    carrier_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    reports_service: ReportsService = Depends(get_reports_service),
):
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
async def get_discrepancy_stats(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    reports_service: ReportsService = Depends(get_reports_service),
):
    """Get discrepancy statistics by type, status, carrier, client"""
    return await reports_service.get_discrepancy_stats(company_id)


@router.post(
    "/export",
    response_model=ExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Export report",
)
async def export_report(
    data: ExportRequest,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    reports_service: ReportsService = Depends(get_reports_service),
):
    """Export report to Excel (returns presigned download URL)"""
    return await reports_service.export_report(company_id, data)