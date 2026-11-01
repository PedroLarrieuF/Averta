"""Contracts module"""
from app.modules.contracts.router import router
from app.modules.contracts.service import ContractsService
from app.modules.contracts.schemas import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    FreightTableCreate,
    FreightTableUpdate,
    FreightTableResponse,
)

__all__ = [
    "router",
    "ContractsService",
    "ContractCreate",
    "ContractUpdate",
    "ContractResponse",
    "ContractListResponse",
    "FreightTableCreate",
    "FreightTableUpdate",
    "FreightTableResponse",
]