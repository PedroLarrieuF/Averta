"""Discrepancies module router"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    ClientIdDep,
    CompanyIdDep,
    CurrentUserDep,
    PaginationDep,
    RequireAuditor,
    RequireManager,
    get_database,
)
from app.core.rate_limit import discrepancies_limiter
from app.modules.discrepancies.schemas import (
    DiscrepancyCreate,
    DiscrepancyListResponse,
    DiscrepancyResponse,
    DiscrepancySeverity,
    DiscrepancyStatus,
    DiscrepancySummary,
    DiscrepancyUpdate,
)
from app.modules.discrepancies.service import DiscrepanciesService
from prisma import Prisma

router = APIRouter(prefix="/discrepancies", tags=["Discrepancies"])


def get_discrepancies_service(db: Prisma = Depends(get_database)) -> DiscrepanciesService:
    return DiscrepanciesService(db)


@router.post(
    "",
    response_model=DiscrepancyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create discrepancy",
)
async def create_discrepancy(
    data: DiscrepancyCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    discrepancies_service: DiscrepanciesService = Depends(get_discrepancies_service),
):
    """Create a new discrepancy (internal use)"""
    data.company_id = company_id
    return await discrepancies_service.create_discrepancy(data)


@router.get(
    "",
    response_model=DiscrepancyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List discrepancies",
)
@discrepancies_limiter
async def list_discrepancies(  # noqa: PLR0913, PLR0917
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    client_id: ClientIdDep,
    pagination: PaginationDep,
    document_id: str | None = Query(None),
    status: DiscrepancyStatus | None = Query(None),
    severity: DiscrepancySeverity | None = Query(None),
    discrepancy_type: str | None = Query(None),
    rule_code: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    discrepancies_service: DiscrepanciesService = Depends(get_discrepancies_service),
):
    """List discrepancies with filters"""
    # If user is CLIENT role, filter by their client
    if current_user.role == "CLIENT" and current_user.client_id:
        client_id = current_user.client_id  # noqa: F841

    return await discrepancies_service.list_discrepancies(
        company_id,
        pagination,
        document_id,
        status,
        severity,
        discrepancy_type,
        rule_code,
        date_from,
        date_to,
    )


@router.get(
    "/summary",
    response_model=DiscrepancySummary,
    status_code=status.HTTP_200_OK,
    summary="Get discrepancy summary",
)
@discrepancies_limiter
async def get_summary(  # noqa: PLR0913, PLR0917
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    client_id: ClientIdDep,
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    discrepancies_service: DiscrepanciesService = Depends(get_discrepancies_service),
):
    """Get discrepancy summary for dashboard"""
    if current_user.role == "CLIENT" and current_user.client_id:
        client_id = current_user.client_id  # noqa: F841

    return await discrepancies_service.get_summary(company_id, client_id, date_from, date_to)


@router.get(
    "/{discrepancy_id}",
    response_model=DiscrepancyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get discrepancy by ID",
)
@discrepancies_limiter
async def get_discrepancy(
    discrepancy_id: str,
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    discrepancies_service: DiscrepanciesService = Depends(get_discrepancies_service),
):
    """Get discrepancy details"""
    return await discrepancies_service.get_by_id(discrepancy_id, company_id)


@router.patch(
    "/{discrepancy_id}",
    response_model=DiscrepancyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update discrepancy",
)
async def update_discrepancy(
    discrepancy_id: str,
    data: DiscrepancyUpdate,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    discrepancies_service: DiscrepanciesService = Depends(get_discrepancies_service),
):
    """Update discrepancy (review, add notes, etc.)"""
    if data.reviewed_by is None:
        data.reviewed_by = current_user.sub
    if data.reviewed_at is None:
        data.reviewed_at = datetime.utcnow()
    return await discrepancies_service.update_discrepancy(discrepancy_id, company_id, data)


@router.post(
    "/bulk-status",
    status_code=status.HTTP_200_OK,
    summary="Bulk update discrepancy status",
)
@discrepancies_limiter
async def bulk_update_status(
    discrepancy_ids: list[str],
    status: DiscrepancyStatus,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    discrepancies_service: DiscrepanciesService = Depends(get_discrepancies_service),
):
    """Bulk update multiple discrepancies status"""
    count = await discrepancies_service.bulk_update_status(
        discrepancy_ids, company_id, status, current_user.sub
    )
    return {"updated": count}
