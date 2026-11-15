"""Companies module service"""

from typing import Any

import structlog

from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import ConflictError
from app.modules.base import BaseService
from app.modules.companies.schemas import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from generated.prisma import Prisma
from generated.prisma.models import Company as CompanyModel

logger = structlog.get_logger()


class CompaniesService(BaseService[CompanyModel, CompanyCreate, CompanyUpdate, CompanyResponse]):
    def __init__(self, db: Prisma):
        super().__init__(db, "Company")

    def _to_response(self, company: CompanyModel) -> CompanyResponse:
        return CompanyResponse(
            id=company.id,
            name=company.name,
            trade_name=company.tradeName,
            cnpj=company.cnpj,
            state_reg=company.stateReg,
            municipal_reg=company.municipalReg,
            address=company.address,
            phone=company.phone,
            email=company.email,
            website=company.website,
            logo_url=company.logoUrl,
            settings=company.settings,
            is_active=company.isActive,
            created_at=company.createdAt,
            updated_at=company.updatedAt,
        )

    async def create_company(self, data: CompanyCreate, user_id: str) -> CompanyResponse:
        """Create new company (super admin only)"""
        # Check CNPJ uniqueness
        existing = await self.db.company.find_unique(where={"cnpj": data.cnpj})
        if existing:
            raise ConflictError("CNPJ already registered")

        create_data = data.model_dump(exclude_unset=True)
        # Convert field names to match Prisma
        if "trade_name" in create_data:
            create_data["tradeName"] = create_data.pop("trade_name")
        if "state_reg" in create_data:
            create_data["stateReg"] = create_data.pop("state_reg")
        if "municipal_reg" in create_data:
            create_data["municipalReg"] = create_data.pop("municipal_reg")
        if "logo_url" in create_data:
            create_data["logoUrl"] = create_data.pop("logo_url")

        company = await self.db.company.create(data=create_data)
        logger.info("company_created", id=company.id, cnpj=company.cnpj, created_by=user_id)
        return self._to_response(company)

    async def update_company(
        self, company_id: str, data: CompanyUpdate, user_id: str
    ) -> CompanyResponse:
        """Update company"""
        await self.get_by_id(company_id, company_id)  # company_id = own company

        update_data = data.model_dump(exclude_unset=True)
        # Convert field names
        field_map = {
            "trade_name": "tradeName",
            "state_reg": "stateReg",
            "municipal_reg": "municipalReg",
            "logo_url": "logoUrl",
            "is_active": "isActive",
        }
        for old, new in field_map.items():
            if old in update_data:
                update_data[new] = update_data.pop(old)

        company = await self.db.company.update(
            where={"id": company_id},
            data=update_data,
        )
        logger.info("company_updated", id=company_id, updated_by=user_id)
        return self._to_response(company)

    async def list_companies(
        self,
        pagination: PaginationParams,
        sort: SortParams,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> CompanyListResponse:
        """List companies (super admin)"""
        where: dict[str, Any] = {}
        if is_active is not None:
            where["isActive"] = is_active
        if search:
            where["OR"] = [
                {"name": {"contains": search, "mode": "insensitive"}},
                {"tradeName": {"contains": search, "mode": "insensitive"}},
                {"cnpj": {"contains": search}},
            ]

        items, total = await self.list("", pagination, sort, where)

        return CompanyListResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    async def get_my_company(self, company_id: str) -> CompanyResponse:
        """Get current user's company"""
        return await self.get_by_id(company_id, company_id)

    async def update_my_company(
        self, company_id: str, data: CompanyUpdate, user_id: str
    ) -> CompanyResponse:
        """Update current user's company (admin only)"""
        return await self.update_company(company_id, data, user_id)
