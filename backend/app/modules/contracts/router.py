"""Contracts module router"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CompanyIdDep,
    PaginationDep,
    RequireAdmin,
    RequireManager,
    SortDep,
    get_database,
)
from app.modules.contracts.schemas import (
    ContractCreate,
    ContractListResponse,
    ContractResponse,
    ContractUpdate,
    FreightTableCreate,
    FreightTableResponse,
    FreightTableUpdate,
)
from app.modules.contracts.service import ContractsService
from prisma import Prisma

router = APIRouter(prefix="/contracts", tags=["Contracts"])


def get_contracts_service(db: Prisma = Depends(get_database)) -> ContractsService:
    return ContractsService(db)


# Contract endpoints
@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new contract",
)
async def create_contract(
    data: ContractCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """Create a new contract"""
    return await contracts_service.create_contract(data, company_id, current_user.sub)


@router.get(
    "",
    response_model=ContractListResponse,
    status_code=status.HTTP_200_OK,
    summary="List contracts",
)
async def list_contracts(  # noqa: PLR0913, PLR0917
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    sort: SortDep,
    status: str | None = Query(None, pattern="^(ACTIVE|EXPIRED|PENDING|CANCELLED)$"),
    carrier_id: str | None = Query(None),
    client_id: str | None = Query(None),
    search: str | None = Query(None),
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """List contracts with pagination and filters"""
    return await contracts_service.list_contracts(
        company_id, pagination, sort, status, carrier_id, client_id, search
    )


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Get contract by ID",
)
async def get_contract(
    contract_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """Get contract details with tables"""
    return await contracts_service.get_by_id(contract_id, company_id)


@router.patch(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Update contract",
)
async def update_contract(
    contract_id: str,
    data: ContractUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """Update contract (admin only)"""
    return await contracts_service.update_contract(contract_id, data, company_id)


# Freight Table endpoints
@router.post(
    "/{contract_id}/tables",
    response_model=FreightTableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create freight table for contract",
)
async def create_freight_table(
    contract_id: str,
    data: FreightTableCreate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """Create a new freight table version for contract"""
    return await contracts_service.create_freight_table(
        contract_id, data, company_id, current_user.sub
    )


@router.get(
    "/{contract_id}/tables",
    response_model=list[FreightTableResponse],
    status_code=status.HTTP_200_OK,
    summary="List freight tables for contract",
)
async def list_freight_tables(
    contract_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    is_active: bool | None = Query(None),
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """List all freight tables for a contract"""
    return await contracts_service.list_freight_tables(contract_id, company_id, is_active)


@router.get(
    "/{contract_id}/tables/active",
    response_model=FreightTableResponse | None,
    status_code=status.HTTP_200_OK,
    summary="Get active freight table for date",
)
async def get_active_freight_table(
    contract_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    date: datetime | None = Query(None),
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """Get the active freight table for a specific date (defaults to now)"""
    return await contracts_service.get_active_freight_table(contract_id, company_id, date)


@router.patch(
    "/{contract_id}/tables/{table_id}",
    response_model=FreightTableResponse,
    status_code=status.HTTP_200_OK,
    summary="Update freight table",
)
async def update_freight_table(  # noqa: PLR0913, PLR0917
    contract_id: str,
    table_id: str,
    data: FreightTableUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    contracts_service: ContractsService = Depends(get_contracts_service),
):
    """Update freight table (admin only)"""
    return await contracts_service.update_freight_table(table_id, data, company_id)
