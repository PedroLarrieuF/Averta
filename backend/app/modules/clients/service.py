"""Clients module service"""

from typing import Any

import structlog

from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.base import BaseService
from app.modules.clients.schemas import (
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)
from generated.prisma import Prisma
from generated.prisma.models import Client as ClientModel

logger = structlog.get_logger()


class ClientsService(BaseService[ClientModel, ClientCreate, ClientUpdate, ClientResponse]):
    def __init__(self, db: Prisma):
        super().__init__(db, "Client")

    def _to_response(self, client: ClientModel) -> ClientResponse:
        return ClientResponse(
            id=client.id,
            company_id=client.companyId,
            user_id=client.userId,
            name=client.name,
            trade_name=client.tradeName,
            cnpj=client.cnpj,
            state_reg=client.stateReg,
            email=client.email,
            phone=client.phone,
            address=client.address,
            contact_person=client.contactPerson,
            contact_email=client.contactEmail,
            contact_phone=client.contactPhone,
            settings=client.settings,
            is_active=client.isActive,
            created_at=client.createdAt,
            updated_at=client.updatedAt,
        )

    async def create_client(
        self, data: ClientCreate, company_id: str, user_id: str
    ) -> ClientResponse:
        """Create new client"""
        # Check CNPJ uniqueness within company
        existing = await self.db.client.find_first(
            where={"cnpj": data.cnpj, "companyId": company_id}
        )
        if existing:
            raise ConflictError("CNPJ already registered for this company")

        # Check user_id uniqueness if provided
        if data.user_id:
            existing_user = await self.db.client.find_unique(where={"userId": data.user_id})
            if existing_user:
                raise ConflictError("User already linked to another client")

        create_data = data.model_dump(exclude_unset=True)
        create_data["companyId"] = company_id
        # Convert field names
        field_map = {
            "trade_name": "tradeName",
            "state_reg": "stateReg",
            "contact_person": "contactPerson",
            "contact_email": "contactEmail",
            "contact_phone": "contactPhone",
            "user_id": "userId",
        }
        for old, new in field_map.items():
            if old in create_data:
                create_data[new] = create_data.pop(old)

        client = await self.db.client.create(data=create_data)
        logger.info(
            "client_created",
            id=client.id,
            cnpj=client.cnpj,
            company_id=company_id,
            created_by=user_id,
        )
        return self._to_response(client)

    async def update_client(
        self, client_id: str, data: ClientUpdate, company_id: str
    ) -> ClientResponse:
        """Update client"""
        await self.get_by_id(client_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        field_map = {
            "trade_name": "tradeName",
            "state_reg": "stateReg",
            "contact_person": "contactPerson",
            "contact_email": "contactEmail",
            "contact_phone": "contactPhone",
            "is_active": "isActive",
        }
        for old, new in field_map.items():
            if old in update_data:
                update_data[new] = update_data.pop(old)

        client = await self.db.client.update(
            where={"id": client_id},
            data=update_data,
        )
        logger.info("client_updated", id=client_id, company_id=company_id)
        return self._to_response(client)

    async def list_clients(
        self,
        company_id: str,
        pagination: PaginationParams,
        sort: SortParams,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> ClientListResponse:
        """List clients"""
        where: dict[str, Any] = {"companyId": company_id}
        if is_active is not None:
            where["isActive"] = is_active
        if search:
            where["OR"] = [
                {"name": {"contains": search, "mode": "insensitive"}},
                {"tradeName": {"contains": search, "mode": "insensitive"}},
                {"cnpj": {"contains": search}},
                {"email": {"contains": search, "mode": "insensitive"}},
            ]

        items, total = await self.list(company_id, pagination, sort, where)

        return ClientListResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    async def get_client_with_relations(self, client_id: str, company_id: str) -> ClientResponse:
        """Get client with branches count"""
        client = await self.db.client.find_first(
            where={"id": client_id, "companyId": company_id},
            include={"branches": True, "contracts": True, "documents": True},
        )
        if not client:
            raise NotFoundError("Client", client_id)
        return self._to_response(client)
