"""Branches module schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BranchCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=1, max_length=20)
    cnpj: str | None = Field(None, min_length=14, max_length=18)
    address: dict[str, Any] | None = None
    client_id: str | None = None


class BranchUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    code: str | None = Field(None, min_length=1, max_length=20)
    cnpj: str | None = Field(None, min_length=14, max_length=18)
    address: dict[str, Any] | None = None
    client_id: str | None = None
    is_active: bool | None = None


class BranchResponse(BaseModel):
    id: str
    company_id: str
    client_id: str | None
    name: str
    code: str
    cnpj: str | None
    address: dict[str, Any] | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BranchListResponse(BaseModel):
    items: list[BranchResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
