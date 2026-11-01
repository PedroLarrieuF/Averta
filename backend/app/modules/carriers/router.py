"""Carriers module router"""
from fastapi import APIRouter, Depends, status, Query
from prisma import Prisma

from app.core.dependencies import (
    get_database,
    CurrentUserDep,
    RequireManager,
    RequireAdmin,
    CompanyIdDep,
    PaginationDep,
    SortDep,
)
from app.modules.carriers.schemas import (
    CarrierCreate,
    CarrierUpdate,
    CarrierResponse,
    CarrierListResponse,
)
from app.modules.carriers.service import CarriersService

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
):
    """Create a new carrier"""
    return await carriers_service.create_carrier(data, company_id, current_user.sub)


@router.get(
    "",
    response_model=CarrierListResponse,
    status_code=status.HTTP_200_OK,
    summary="List carriers",
)
async def list_carriers(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    sort: SortDep,
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    carriers_service: CarriersService = Depends(get_carriers_service),
):
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
):
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
):
    """Update carrier (admin only)"""
    return await carriers_service.update_carrier(carrier_id, data, company_id)