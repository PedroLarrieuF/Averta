"""Users module service"""


import bcrypt
import structlog

from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import ConflictError
from app.modules.base import BaseService
from app.modules.users.schemas import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from prisma import Prisma

logger = structlog.get_logger()


class UsersService(BaseService):
    def __init__(self, db: Prisma):
        super().__init__(db, "User")

    def _to_response(self, user) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.fullName,
            role=user.role,
            status=user.status,
            company_id=user.companyId,
            client_id=user.clientId,
            avatar_url=user.avatarUrl,
            last_login_at=user.lastLoginAt,
            created_at=user.createdAt,
            updated_at=user.updatedAt,
        )

    async def create_user(self, data: UserCreate, company_id: str, created_by: str) -> UserResponse:
        """Create new user (admin only)"""
        # Check email uniqueness within company
        existing = await self.db.user.find_first(
            where={"email": data.email, "companyId": company_id}
        )
        if existing:
            raise ConflictError("Email already exists in this company")

        # Hash password if provided
        password_hash = None
        if data.password:
            password_hash = bcrypt.hash(data.password.encode()).decode()

        create_data = data.model_dump(exclude={"password"}, exclude_unset=True)
        create_data["companyId"] = company_id
        create_data["passwordHash"] = password_hash
        create_data["status"] = "ACTIVE"

        user = await self.db.user.create(data=create_data)
        logger.info("user_created", id=user.id, email=user.email, created_by=created_by)
        return self._to_response(user)

    async def update_user(self, user_id: str, data: UserUpdate, company_id: str) -> UserResponse:
        """Update user"""
        await self.get_by_id(user_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        if "full_name" in update_data:
            update_data["fullName"] = update_data.pop("full_name")
        if "avatar_url" in update_data:
            update_data["avatarUrl"] = update_data.pop("avatar_url")

        user = await self.db.user.update(
            where={"id": user_id},
            data=update_data,
        )
        logger.info("user_updated", id=user_id, company_id=company_id)
        return self._to_response(user)

    async def list_users(
        self,
        company_id: str,
        pagination: PaginationParams,
        sort: SortParams,
        role: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> UserListResponse:
        """List users with filters"""
        where: dict = {"companyId": company_id}
        if role:
            where["role"] = role
        if status:
            where["status"] = status
        if search:
            where["OR"] = [
                {"email": {"contains": search, "mode": "insensitive"}},
                {"fullName": {"contains": search, "mode": "insensitive"}},
            ]

        items, total = await self.list(company_id, pagination, sort, where)

        return UserListResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    async def deactivate_user(self, user_id: str, company_id: str, deactivated_by: str) -> None:
        """Deactivate user (soft delete)"""
        await self.get_by_id(user_id, company_id)
        await self.db.user.update(
            where={"id": user_id},
            data={"status": "INACTIVE"},
        )
        logger.info("user_deactivated", id=user_id, deactivated_by=deactivated_by)

    async def reset_password(self, user_id: str, company_id: str, new_password: str) -> None:
        """Admin reset user password"""
        await self.get_by_id(user_id, company_id)
        password_hash = bcrypt.hash(new_password.encode()).decode()
        await self.db.user.update(
            where={"id": user_id},
            data={"passwordHash": password_hash},
        )
        logger.info("user_password_reset_by_admin", id=user_id, company_id=company_id)
