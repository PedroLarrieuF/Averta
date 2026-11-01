"""Branches module schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BranchCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=1, max_length=20)
    cnpj: Optional[str] = Field(None, min_length=14, max_length=18)
    address: Optional[dict] = None
    client_id: Optional[str] = None


class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    cnpj: Optional[str] = Field(None, min_length=14, max_length=18)
    address: Optional[dict] = None
    client_id: Optional[str] = None
    is_active: Optional[bool] = None


class BranchResponse(BaseModel):
    id: str
    company_id: str
    client_id: Optional[str]
    name: str
    code: str
    cnpj: Optional[str]
    address: Optional[dict]
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