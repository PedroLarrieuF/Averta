"""Carriers module service"""

import structlog

from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import ConflictError
from app.modules.base import BaseService
from app.modules.carriers.schemas import (
    CarrierCreate,
    CarrierListResponse,
    CarrierResponse,
    CarrierUpdate,
)
from prisma import Prisma

logger = structlog.get_logger()


class CarriersService(BaseService):
    def __init__(self, db: Prisma):
        super().__init__(db, "Carrier")

    def _to_response(self, carrier) -> CarrierResponse:
        return CarrierResponse(
            id=carrier.id,
            company_id=carrier.companyId,
            name=carrier.name,
            trade_name=carrier.tradeName,
            cnpj=carrier.cnpj,
            state_reg=carrier.stateReg,
            address=carrier.address,
            contact_person=carrier.contactPerson,
            contact_email=carrier.contactEmail,
            contact_phone=carrier.contactPhone,
            bank_info=carrier.bankInfo,
            settings=carrier.settings,
            is_active=carrier.isActive,
            created_at=carrier.createdAt,
            updated_at=carrier.updatedAt,
        )

    async def create_carrier(
        self, data: CarrierCreate, company_id: str, user_id: str
    ) -> CarrierResponse:
        """Create new carrier"""
        existing = await self.db.carrier.find_first(
            where={"cnpj": data.cnpj, "companyId": company_id}
        )
        if existing:
            raise ConflictError("CNPJ already registered for this company")

        create_data = data.model_dump(exclude_unset=True)
        create_data["companyId"] = company_id
        field_map = {
            "trade_name": "tradeName",
            "state_reg": "stateReg",
            "contact_person": "contactPerson",
            "contact_email": "contactEmail",
            "contact_phone": "contactPhone",
            "bank_info": "bankInfo",
        }
        for old, new in field_map.items():
            if old in create_data:
                create_data[new] = create_data.pop(old)

        carrier = await self.db.carrier.create(data=create_data)
        logger.info(
            "carrier_created",
            id=carrier.id,
            cnpj=carrier.cnpj,
            company_id=company_id,
            created_by=user_id,
        )
        return self._to_response(carrier)

    async def update_carrier(
        self, carrier_id: str, data: CarrierUpdate, company_id: str
    ) -> CarrierResponse:
        """Update carrier"""
        await self.get_by_id(carrier_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        field_map = {
            "trade_name": "tradeName",
            "state_reg": "stateReg",
            "contact_person": "contactPerson",
            "contact_email": "contactEmail",
            "contact_phone": "contactPhone",
            "bank_info": "bankInfo",
            "is_active": "isActive",
        }
        for old, new in field_map.items():
            if old in update_data:
                update_data[new] = update_data.pop(old)

        carrier = await self.db.carrier.update(
            where={"id": carrier_id},
            data=update_data,
        )
        logger.info("carrier_updated", id=carrier_id, company_id=company_id)
        return self._to_response(carrier)

    async def list_carriers(
        self,
        company_id: str,
        pagination: PaginationParams,
        sort: SortParams,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> CarrierListResponse:
        """List carriers"""
        where: dict = {"companyId": company_id}
        if is_active is not None:
            where["isActive"] = is_active
        if search:
            where["OR"] = [
                {"name": {"contains": search, "mode": "insensitive"}},
                {"tradeName": {"contains": search, "mode": "insensitive"}},
                {"cnpj": {"contains": search}},
            ]

        items, total = await self.list(company_id, pagination, sort, where)

        return CarrierListResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )
