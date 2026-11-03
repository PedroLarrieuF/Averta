"""Clients module"""

from app.modules.clients.router import router
from app.modules.clients.schemas import (
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)
from app.modules.clients.service import ClientsService

__all__ = [
    "router",
    "ClientsService",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientListResponse",
]
