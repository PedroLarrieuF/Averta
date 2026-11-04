"""Branches module router"""

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CompanyIdDep,
    PaginationDep,
    RequireAdmin,
    RequireManager,
    SortDep,
    get_database,
)
from app.modules.branches.schemas import (
    BranchCreate,
    BranchListResponse,
    BranchResponse,
    BranchUpdate,
)
from app.modules.branches.service import BranchesService
from prisma import Prisma

router = APIRouter(prefix="/branches", tags=["Branches"])


def get_branches_service(db: Prisma = Depends(get_database)) -> BranchesService:
    return BranchesService(db)


@router.post(
    "",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new branch",
)
async def create_branch(
    data: BranchCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    branches_service: BranchesService = Depends(get_branches_service),
) -> BranchResponse:
    """Create a new branch"""
    return await branches_service.create_branch(data, company_id, current_user.sub)


@router.get(
    "",
    response_model=BranchListResponse,
    status_code=status.HTTP_200_OK,
    summary="List branches",
)
async def list_branches(  # noqa: PLR0913, PLR0917
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    sort: SortDep,
    client_id: str | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    branches_service: BranchesService = Depends(get_branches_service),
) -> BranchListResponse:
    """List branches with pagination and filters"""
    return await branches_service.list_branches(
        company_id, pagination, sort, client_id, is_active, search
    )


@router.get(
    "/{branch_id}",
    response_model=BranchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get branch by ID",
)
async def get_branch(
    branch_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    branches_service: BranchesService = Depends(get_branches_service),
) -> BranchResponse:
    """Get branch details"""
    return await branches_service.get_by_id(branch_id, company_id)


@router.patch(
    "/{branch_id}",
    response_model=BranchResponse,
    status_code=status.HTTP_200_OK,
    summary="Update branch",
)
async def update_branch(
    branch_id: str,
    data: BranchUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    branches_service: BranchesService = Depends(get_branches_service),
) -> BranchResponse:
    """Update branch (admin only)"""
    return await branches_service.update_branch(branch_id, data, company_id)
