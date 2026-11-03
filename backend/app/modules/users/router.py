"""Users module router"""

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CompanyIdDep,
    PaginationDep,
    RequireAdmin,
    RequireManager,
    SortDep,
    get_database,
)
from app.modules.users.schemas import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import UsersService
from prisma import Prisma

router = APIRouter(prefix="/users", tags=["Users"])


def get_users_service(db: Prisma = Depends(get_database)) -> UsersService:
    return UsersService(db)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
)
async def create_user(
    data: UserCreate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    users_service: UsersService = Depends(get_users_service),
):
    """Create a new user (admin only)"""
    return await users_service.create_user(data, company_id, current_user.sub)


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List users",
)
async def list_users(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    sort: SortDep,
    role: str | None = Query(None, pattern="^(ADMIN|AUDITOR|MANAGER|CLIENT)$"),
    status: str | None = Query(None, pattern="^(ACTIVE|INACTIVE|PENDING|BLOCKED)$"),
    search: str | None = Query(None),
    users_service: UsersService = Depends(get_users_service),
):
    """List users with pagination and filters"""
    return await users_service.list_users(company_id, pagination, sort, role, status, search)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
)
async def get_user(
    user_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    users_service: UsersService = Depends(get_users_service),
):
    """Get user details"""
    return await users_service.get_by_id(user_id, company_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user",
)
async def update_user(
    user_id: str,
    data: UserUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    users_service: UsersService = Depends(get_users_service),
):
    """Update user (admin only)"""
    return await users_service.update_user(user_id, data, company_id)


@router.post(
    "/{user_id}/deactivate",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate user",
)
async def deactivate_user(
    user_id: str,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    users_service: UsersService = Depends(get_users_service),
):
    """Deactivate user (admin only)"""
    await users_service.deactivate_user(user_id, company_id, current_user.sub)


@router.post(
    "/{user_id}/reset-password",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset user password (admin)",
)
async def reset_password(
    user_id: str,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    new_password: str = Query(..., min_length=8, max_length=128),
    users_service: UsersService = Depends(get_users_service),
):
    """Reset user password (admin only)"""
    await users_service.reset_password(user_id, company_id, new_password)
