"""Branches module service"""

from typing import Any

import structlog

from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.base import BaseService
from app.modules.branches.schemas import (
    BranchCreate,
    BranchListResponse,
    BranchResponse,
    BranchUpdate,
)
from prisma import Prisma
from prisma.models import Branch as BranchModel

logger = structlog.get_logger()


class BranchesService(BaseService[BranchModel, BranchCreate, BranchUpdate, BranchResponse]):
    def __init__(self, db: Prisma):
        super().__init__(db, "Branch")

    def _to_response(self, branch: BranchModel) -> BranchResponse:
        return BranchResponse(
            id=branch.id,
            company_id=branch.companyId,
            client_id=branch.clientId,
            name=branch.name,
            code=branch.code,
            cnpj=branch.cnpj,
            address=branch.address,
            is_active=branch.isActive,
            created_at=branch.createdAt,
            updated_at=branch.updatedAt,
        )

    async def create_branch(
        self, data: BranchCreate, company_id: str, user_id: str
    ) -> BranchResponse:
        """Create new branch"""
        existing = await self.db.branch.find_first(
            where={"code": data.code, "companyId": company_id}
        )
        if existing:
            raise ConflictError("Branch code already exists for this company")

        if data.client_id:
            client = await self.db.client.find_first(
                where={"id": data.client_id, "companyId": company_id}
            )
            if not client:
                raise NotFoundError("Client", data.client_id)

        create_data = data.model_dump(exclude_unset=True)
        create_data["companyId"] = company_id
        if "client_id" in create_data:
            create_data["clientId"] = create_data.pop("client_id")

        branch = await self.db.branch.create(data=create_data)
        logger.info(
            "branch_created",
            id=branch.id,
            code=branch.code,
            company_id=company_id,
            created_by=user_id,
        )
        return self._to_response(branch)

    async def update_branch(
        self, branch_id: str, data: BranchUpdate, company_id: str
    ) -> BranchResponse:
        """Update branch"""
        await self.get_by_id(branch_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        field_map = {
            "client_id": "clientId",
            "is_active": "isActive",
        }
        for old, new in field_map.items():
            if old in update_data:
                update_data[new] = update_data.pop(old)

        if "clientId" in update_data and update_data["clientId"]:
            client = await self.db.client.find_first(
                where={"id": update_data["clientId"], "companyId": company_id}
            )
            if not client:
                raise NotFoundError("Client", update_data["clientId"])

        branch = await self.db.branch.update(
            where={"id": branch_id},
            data=update_data,
        )
        logger.info("branch_updated", id=branch_id, company_id=company_id)
        return self._to_response(branch)

    async def list_branches(  # noqa: PLR0913, PLR0917
        self,
        company_id: str,
        pagination: PaginationParams,
        sort: SortParams,
        client_id: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> BranchListResponse:
        """List branches"""
        where: dict[str, Any] = {"companyId": company_id}
        if client_id:
            where["clientId"] = client_id
        if is_active is not None:
            where["isActive"] = is_active
        if search:
            where["OR"] = [
                {"name": {"contains": search, "mode": "insensitive"}},
                {"code": {"contains": search}},
            ]

        items, total = await self.list(company_id, pagination, sort, where)

        return BranchListResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )
