"""Carriers module router"""

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CompanyIdDep,
    PaginationDep,
    RequireAdmin,
    RequireManager,
    SortDep,
    get_database,
)
from app.modules.carriers.schemas import (
    CarrierCreate,
    CarrierListResponse,
    CarrierResponse,
    CarrierUpdate,
)
from app.modules.carriers.service import CarriersService
from prisma import Prisma

router = APIRouter(prefix="/carriers", tags=["Carriers"])


def get_carriers_service(db: Prisma = Depends(get_database)) -> CarriersService:
    return CarriersService(db)


@router.post(
    "",
    response_model=CarrierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new carrier",
)
async def create_carrier(
    data: CarrierCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    carriers_service: CarriersService = Depends(get_carriers_service),
) -> CarrierResponse:
    """Create a new carrier"""
    return await carriers_service.create_carrier(data, company_id, current_user.sub)


@router.get(
    "",
    response_model=CarrierListResponse,
    status_code=status.HTTP_200_OK,
    summary="List carriers",
)
async def list_carriers(  # noqa: PLR0913, PLR0917
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    sort: SortDep,
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    carriers_service: CarriersService = Depends(get_carriers_service),
) -> CarrierListResponse:
    """List carriers with pagination and filters"""
    return await carriers_service.list_carriers(company_id, pagination, sort, is_active, search)


@router.get(
    "/{carrier_id}",
    response_model=CarrierResponse,
    status_code=status.HTTP_200_OK,
    summary="Get carrier by ID",
)
async def get_carrier(
    carrier_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    carriers_service: CarriersService = Depends(get_carriers_service),
) -> CarrierResponse:
    """Get carrier details"""
    return await carriers_service.get_by_id(carrier_id, company_id)


@router.patch(
    "/{carrier_id}",
    response_model=CarrierResponse,
    status_code=status.HTTP_200_OK,
    summary="Update carrier",
)
async def update_carrier(
    carrier_id: str,
    data: CarrierUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    carriers_service: CarriersService = Depends(get_carriers_service),
) -> CarrierResponse:
    """Update carrier (admin only)"""
    return await carriers_service.update_carrier(carrier_id, data, company_id)
