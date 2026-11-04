"""Contracts module service"""

from datetime import datetime

import structlog

from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.base import BaseService
from app.modules.contracts.schemas import (
    ContractCreate,
    ContractListResponse,
    ContractResponse,
    ContractUpdate,
    FreightTableCreate,
    FreightTableResponse,
    FreightTableUpdate,
)
from app.services.rules_engine_v2 import get_engine_instance
from prisma import Prisma

logger = structlog.get_logger()

# Constants
PROGRESSIVE_MONTH_DAYS = 30


class ContractsService(BaseService):
    def __init__(self, db: Prisma):
        super().__init__(db, "Contract")

    def _to_response(self, contract) -> ContractResponse:
        tables = [
            FreightTableResponse(
                id=t.id,
                contract_id=t.contractId,
                name=t.name,
                version=t.version,
                effective_from=t.effectiveFrom,
                effective_to=t.effectiveTo,
                description=t.description,
                rules=t.rules,
                is_active=t.isActive,
                created_at=t.createdAt,
                updated_at=t.updatedAt,
            )
            for t in getattr(contract, "tables", [])
        ]
        return ContractResponse(
            id=contract.id,
            company_id=contract.companyId,
            client_id=contract.clientId,
            carrier_id=contract.carrierId,
            number=contract.number,
            description=contract.description,
            status=contract.status,
            start_date=contract.startDate,
            end_date=contract.endDate,
            success_fee_pct=contract.successFeePct,
            min_recovery=contract.minRecovery,
            currency=contract.currency,
            terms=contract.terms,
            metadata=contract.metadata,
            created_at=contract.createdAt,
            updated_at=contract.updatedAt,
            tables=tables,
            # Progressive pricing fields
            pricing_model=getattr(contract, "pricingModel", "FIXED"),
            progressive_start_date=getattr(contract, "progressiveStartDate", None),
            progressive_month1_pct=getattr(contract, "progressiveMonth1Pct", 5.0),
            progressive_month2_pct=getattr(contract, "progressiveMonth2Pct", 10.0),
        )

    async def create_contract(
        self, data: ContractCreate, company_id: str, user_id: str
    ) -> ContractResponse:
        """Create new contract"""
        existing = await self.db.contract.find_first(
            where={"number": data.number, "companyId": company_id}
        )
        if existing:
            raise ConflictError("Contract number already exists for this company")

        # Validate carrier belongs to company
        carrier = await self.db.carrier.find_first(
            where={"id": data.carrier_id, "companyId": company_id}
        )
        if not carrier:
            raise NotFoundError("Carrier", data.carrier_id)

        if data.client_id:
            client = await self.db.client.find_first(
                where={"id": data.client_id, "companyId": company_id}
            )
            if not client:
                raise NotFoundError("Client", data.client_id)

        create_data = data.model_dump(exclude_unset=True)
        create_data["companyId"] = company_id
        field_map = {
            "client_id": "clientId",
            "carrier_id": "carrierId",
            "start_date": "startDate",
            "end_date": "endDate",
            "success_fee_pct": "successFeePct",
            "min_recovery": "minRecovery",
            "pricing_model": "pricingModel",
            "progressive_start_date": "progressiveStartDate",
            "progressive_month1_pct": "progressiveMonth1Pct",
            "progressive_month2_pct": "progressiveMonth2Pct",
        }
        for old, new in field_map.items():
            if old in create_data:
                create_data[new] = create_data.pop(old)

        contract = await self.db.contract.create(
            data=create_data,
            include={"tables": True},
        )
        logger.info(
            "contract_created",
            id=contract.id,
            number=contract.number,
            company_id=company_id,
            created_by=user_id,
        )
        return self._to_response(contract)

    async def update_contract(
        self, contract_id: str, data: ContractUpdate, company_id: str
    ) -> ContractResponse:
        """Update contract"""
        await self.get_by_id(contract_id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        field_map = {
            "client_id": "clientId",
            "carrier_id": "carrierId",
            "start_date": "startDate",
            "end_date": "endDate",
            "success_fee_pct": "successFeePct",
            "min_recovery": "minRecovery",
            "pricing_model": "pricingModel",
            "progressive_start_date": "progressiveStartDate",
            "progressive_month1_pct": "progressiveMonth1Pct",
            "progressive_month2_pct": "progressiveMonth2Pct",
        }
        for old, new in field_map.items():
            if old in update_data:
                update_data[new] = update_data.pop(old)

        if "carrierId" in update_data:
            carrier = await self.db.carrier.find_first(
                where={"id": update_data["carrierId"], "companyId": company_id}
            )
            if not carrier:
                raise NotFoundError("Carrier", update_data["carrierId"])

        if "clientId" in update_data and update_data["clientId"]:
            client = await self.db.client.find_first(
                where={"id": update_data["clientId"], "companyId": company_id}
            )
            if not client:
                raise NotFoundError("Client", update_data["clientId"])

        contract = await self.db.contract.update(
            where={"id": contract_id},
            data=update_data,
            include={"tables": True},
        )
        logger.info("contract_updated", id=contract_id, company_id=company_id)
        return self._to_response(contract)

    async def list_contracts(  # noqa: PLR0913, PLR0917
        self,
        company_id: str,
        pagination: PaginationParams,
        sort: SortParams,
        status: str | None = None,
        carrier_id: str | None = None,
        client_id: str | None = None,
        search: str | None = None,
    ) -> ContractListResponse:
        """List contracts"""
        where: dict = {"companyId": company_id}
        if status:
            where["status"] = status
        if carrier_id:
            where["carrierId"] = carrier_id
        if client_id:
            where["clientId"] = client_id
        if search:
            where["OR"] = [
                {"number": {"contains": search, "mode": "insensitive"}},
                {"description": {"contains": search, "mode": "insensitive"}},
            ]

        items, total = await self.list(company_id, pagination, sort, where)

        return ContractListResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    # Freight Tables
    async def create_freight_table(
        self, contract_id: str, data: FreightTableCreate, company_id: str, user_id: str
    ) -> FreightTableResponse:
        """Create freight table for contract"""
        await self.get_by_id(contract_id, company_id)

        table = await self.db.freightTable.create(
            data={
                "contractId": contract_id,
                "name": data.name,
                "version": data.version,
                "effectiveFrom": data.effective_from,
                "effectiveTo": data.effective_to,
                "description": data.description,
                "rules": data.rules,
            }
        )

        # Invalidate rules engine cache for freight-related rules
        engine = get_engine_instance()
        if engine:
            await engine.invalidate_freight_table_cache()
            logger.info("rules_cache_invalidated_after_freight_table_create", table_id=table.id)

        logger.info(
            "freight_table_created", id=table.id, contract_id=contract_id, created_by=user_id
        )
        return FreightTableResponse(
            id=table.id,
            contract_id=table.contractId,
            name=table.name,
            version=table.version,
            effective_from=table.effectiveFrom,
            effective_to=table.effectiveTo,
            description=table.description,
            rules=table.rules,
            is_active=table.isActive,
            created_at=table.createdAt,
            updated_at=table.updatedAt,
        )

    async def update_freight_table(
        self, table_id: str, data: FreightTableUpdate, company_id: str
    ) -> FreightTableResponse:
        """Update freight table"""
        table = await self.db.freightTable.find_first(
            where={"id": table_id, "contract": {"companyId": company_id}}
        )
        if not table:
            raise NotFoundError("FreightTable", table_id)

        update_data = data.model_dump(exclude_unset=True)
        field_map = {
            "effective_from": "effectiveFrom",
            "effective_to": "effectiveTo",
            "is_active": "isActive",
        }
        for old, new in field_map.items():
            if old in update_data:
                update_data[new] = update_data.pop(old)

        table = await self.db.freightTable.update(
            where={"id": table_id},
            data=update_data,
        )

        # Invalidate rules engine cache for freight-related rules
        engine = get_engine_instance()
        if engine:
            await engine.invalidate_freight_table_cache()
            logger.info("rules_cache_invalidated_after_freight_table_update", table_id=table_id)

        logger.info("freight_table_updated", id=table_id, company_id=company_id)
        return FreightTableResponse(
            id=table.id,
            contract_id=table.contractId,
            name=table.name,
            version=table.version,
            effective_from=table.effectiveFrom,
            effective_to=table.effectiveTo,
            description=table.description,
            rules=table.rules,
            is_active=table.isActive,
            created_at=table.createdAt,
            updated_at=table.updatedAt,
        )

    async def list_freight_tables(
        self, contract_id: str, company_id: str, is_active: bool | None = None
    ) -> list[FreightTableResponse]:
        """List freight tables for contract"""
        await self.get_by_id(contract_id, company_id)

        where = {"contractId": contract_id}
        if is_active is not None:
            where["isActive"] = is_active

        tables = await self.db.freightTable.find_many(
            where=where,
            order={"effectiveFrom": "desc"},
        )
        return [
            FreightTableResponse(
                id=t.id,
                contract_id=t.contractId,
                name=t.name,
                version=t.version,
                effective_from=t.effectiveFrom,
                effective_to=t.effectiveTo,
                description=t.description,
                rules=t.rules,
                is_active=t.isActive,
                created_at=t.createdAt,
                updated_at=t.updatedAt,
            )
            for t in tables
        ]

    async def get_active_freight_table(
        self, contract_id: str, company_id: str, date: datetime | None = None
    ):
        """Get active freight table for a given date"""
        check_date = date or datetime.utcnow()

        await self.get_by_id(contract_id, company_id)

        table = await self.db.freightTable.find_first(
            where={
                "contractId": contract_id,
                "isActive": True,
                "effectiveFrom": {"lte": check_date},
                "OR": [
                    {"effectiveTo": None},
                    {"effectiveTo": {"gte": check_date}},
                ],
            },
            order={"effectiveFrom": "desc"},
        )
        if not table:
            return None

        return FreightTableResponse(
            id=table.id,
            contract_id=table.contractId,
            name=table.name,
            version=table.version,
            effective_from=table.effectiveFrom,
            effective_to=table.effectiveTo,
            description=table.description,
            rules=table.rules,
            is_active=table.isActive,
            created_at=table.createdAt,
            updated_at=table.updatedAt,
        )

    def calculate_progressive_fee_pct(
        self, contract, reference_date: datetime | None = None
    ) -> float:
        """
        Calculate the success fee percentage based on progressive pricing model.

        For PROGRESSIVE model:
        - Month 1 (first 30 days from progressive_start_date or start_date): progressive_month1_pct (default 5%)
        - Month 2 onwards: progressive_month2_pct (default 10%)

        For FIXED model: returns the standard success_fee_pct
        """
        if contract.pricingModel == "FIXED":
            return contract.successFeePct

        # PROGRESSIVE model
        start_date = contract.progressiveStartDate or contract.startDate
        if not start_date:
            return contract.successFeePct

        check_date = reference_date or datetime.utcnow()

        # Calculate months difference
        # Month 1 = first 30 days (0-29 days)
        # Month 2+ = 30+ days
        days_diff = (check_date - start_date).days

        if days_diff < PROGRESSIVE_MONTH_DAYS:
            return contract.progressiveMonth1Pct or 5.0
        else:
            return contract.progressiveMonth2Pct or 10.0
