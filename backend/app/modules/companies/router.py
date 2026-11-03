"""Companies module router"""

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CompanyIdDep,
    CurrentUserDep,
    PaginationDep,
    RequireAdmin,
    SortDep,
    get_database,
)
from app.modules.companies.schemas import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.modules.companies.service import CompaniesService
from prisma import Prisma

router = APIRouter(prefix="/companies", tags=["Companies"])


def get_companies_service(db: Prisma = Depends(get_database)) -> CompaniesService:
    return CompaniesService(db)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new company (super admin)",
)
async def create_company(
    data: CompanyCreate,
    current_user: RequireAdmin,
    companies_service: CompaniesService = Depends(get_companies_service),
):
    """Create a new company (super admin only)"""
    return await companies_service.create_company(data, current_user.sub)


@router.get(
    "",
    response_model=CompanyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List companies (super admin)",
)
async def list_companies(
    current_user: RequireAdmin,
    pagination: PaginationDep,
    sort: SortDep,
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    companies_service: CompaniesService = Depends(get_companies_service),
):
    """List all companies (super admin)"""
    return await companies_service.list_companies(pagination, sort, is_active, search)


@router.get(
    "/me",
    response_model=CompanyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get my company",
)
async def get_my_company(
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    companies_service: CompaniesService = Depends(get_companies_service),
):
    """Get current user's company"""
    return await companies_service.get_my_company(company_id)


@router.patch(
    "/me",
    response_model=CompanyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update my company (admin)",
)
async def update_my_company(
    data: CompanyUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    companies_service: CompaniesService = Depends(get_companies_service),
):
    """Update current user's company (admin only)"""
    return await companies_service.update_my_company(company_id, data, current_user.sub)


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get company by ID (super admin)",
)
async def get_company(
    company_id: str,
    current_user: RequireAdmin,
    companies_service: CompaniesService = Depends(get_companies_service),
):
    """Get company by ID (super admin)"""
    return await companies_service.get_by_id(company_id, company_id)


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update company (super admin)",
)
async def update_company(
    company_id: str,
    data: CompanyUpdate,
    current_user: RequireAdmin,
    companies_service: CompaniesService = Depends(get_companies_service),
):
    """Update company (super admin)"""
    return await companies_service.update_company(company_id, data, current_user.sub)
