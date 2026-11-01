"""Clients module router"""
from fastapi import APIRouter, Depends, status, Query
from prisma import Prisma

from app.core.dependencies import (
    get_database,
    CurrentUserDep,
    RequireManager,
    RequireAdmin,
    CompanyIdDep,
    PaginationDep,
    SortDep,
)
from app.modules.clients.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
)
from app.modules.clients.service import ClientsService

router = APIRouter(prefix="/clients", tags=["Clients"])


def get_clients_service(db: Prisma = Depends(get_database)) -> ClientsService:
    return ClientsService(db)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new client",
)
async def create_client(
    data: ClientCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    clients_service: ClientsService = Depends(get_clients_service),
):
    """Create a new client"""
    return await clients_service.create_client(data, company_id, current_user.sub)


@router.get(
    "",
    response_model=ClientListResponse,
    status_code=status.HTTP_200_OK,
    summary="List clients",
)
async def list_clients(
    current_user: RequireManager,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    sort: SortDep,
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    clients_service: ClientsService = Depends(get_clients_service),
):
    """List clients with pagination and filters"""
    return await clients_service.list_clients(company_id, pagination, sort, is_active, search)


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
    summary="Get client by ID",
)
async def get_client(
    client_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    clients_service: ClientsService = Depends(get_clients_service),
):
    """Get client details"""
    return await clients_service.get_by_id(client_id, company_id)


@router.get(
    "/{client_id}/details",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
    summary="Get client with relations",
)
async def get_client_details(
    client_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    clients_service: ClientsService = Depends(get_clients_service),
):
    """Get client with branches, contracts, documents count"""
    return await clients_service.get_client_with_relations(client_id, company_id)


@router.patch(
    "/{client_id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
    summary="Update client",
)
async def update_client(
    client_id: str,
    data: ClientUpdate,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    clients_service: ClientsService = Depends(get_clients_service),
):
    """Update client (admin only)"""
    return await clients_service.update_client(client_id, data, company_id)


@router.post(
    "/{client_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate client",
)
async def deactivate_client(
    client_id: str,
    current_user: RequireAdmin,
    company_id: CompanyIdDep,
    clients_service: ClientsService = Depends(get_clients_service),
):
    """Deactivate client (admin only)"""
    await clients_service.update_client(
        client_id, ClientUpdate(is_active=False), company_id
    )