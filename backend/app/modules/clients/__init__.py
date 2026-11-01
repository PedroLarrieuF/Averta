"""Clients module"""
from app.modules.clients.router import router
from app.modules.clients.service import ClientsService
from app.modules.clients.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
)

__all__ = [
    "router",
    "ClientsService",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientListResponse",
]