"""Contracts module schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class FreightTableCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    version: str = Field(..., min_length=1, max_length=50)
    effective_from: datetime
    effective_to: Optional[datetime] = None
    description: Optional[str] = None
    rules: dict  # JSON: {faixas_peso, pedagios, advalorem, gris, difal, etc.}


class FreightTableUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    description: Optional[str] = None
    rules: Optional[dict] = None
    is_active: Optional[bool] = None


class FreightTableResponse(BaseModel):
    id: str
    contract_id: str
    name: str
    version: str
    effective_from: datetime
    effective_to: Optional[datetime]
    description: Optional[str]
    rules: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    client_id: Optional[str] = None
    carrier_id: str
    number: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    success_fee_pct: float = Field(default=25.0, ge=0, le=100)
    min_recovery: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    terms: Optional[dict] = None
    metadata: Optional[dict] = None
    # Progressive pricing fields
    pricing_model: str = Field(default="FIXED", pattern="^(FIXED|PROGRESSIVE)$")
    progressive_start_date: Optional[datetime] = None
    progressive_month1_pct: float = Field(default=5.0, ge=0, le=100)
    progressive_month2_pct: float = Field(default=10.0, ge=0, le=100)


class ContractUpdate(BaseModel):
    client_id: Optional[str] = None
    carrier_id: Optional[str] = None
    number: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    success_fee_pct: Optional[float] = Field(None, ge=0, le=100)
    min_recovery: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    terms: Optional[dict] = None
    metadata: Optional[dict] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|EXPIRED|PENDING|CANCELLED)$")
    # Progressive pricing fields
    pricing_model: Optional[str] = Field(None, pattern="^(FIXED|PROGRESSIVE)$")
    progressive_start_date: Optional[datetime] = None
    progressive_month1_pct: Optional[float] = Field(None, ge=0, le=100)
    progressive_month2_pct: Optional[float] = Field(None, ge=0, le=100)


class ContractResponse(BaseModel):
    id: str
    company_id: str
    client_id: Optional[str]
    carrier_id: str
    number: str
    description: Optional[str]
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    success_fee_pct: float
    min_recovery: Optional[float]
    currency: str
    terms: Optional[dict]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime
    tables: list[FreightTableResponse] = []
    # Progressive pricing fields
    pricing_model: str
    progressive_start_date: Optional[datetime]
    progressive_month1_pct: float
    progressive_month2_pct: float

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    items: list[ContractResponse]
    total: int
    page: int
    page_size: int
    total_pages: int