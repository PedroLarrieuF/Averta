"""Contracts module schemas"""

from datetime import datetime

from pydantic import BaseModel, Field


class FreightTableCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    version: str = Field(..., min_length=1, max_length=50)
    effective_from: datetime
    effective_to: datetime | None = None
    description: str | None = None
    rules: dict  # JSON: {faixas_peso, pedagios, advalorem, gris, difal, etc.}


class FreightTableUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    version: str | None = Field(None, min_length=1, max_length=50)
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    description: str | None = None
    rules: dict | None = None
    is_active: bool | None = None


class FreightTableResponse(BaseModel):
    id: str
    contract_id: str
    name: str
    version: str
    effective_from: datetime
    effective_to: datetime | None
    description: str | None
    rules: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    client_id: str | None = None
    carrier_id: str
    number: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    start_date: datetime
    end_date: datetime | None = None
    success_fee_pct: float = Field(default=25.0, ge=0, le=100)
    min_recovery: float | None = Field(None, ge=0)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    terms: dict | None = None
    metadata: dict | None = None
    # Progressive pricing fields
    pricing_model: str = Field(default="FIXED", pattern="^(FIXED|PROGRESSIVE)$")
    progressive_start_date: datetime | None = None
    progressive_month1_pct: float = Field(default=5.0, ge=0, le=100)
    progressive_month2_pct: float = Field(default=10.0, ge=0, le=100)


class ContractUpdate(BaseModel):
    client_id: str | None = None
    carrier_id: str | None = None
    number: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    success_fee_pct: float | None = Field(None, ge=0, le=100)
    min_recovery: float | None = Field(None, ge=0)
    currency: str | None = Field(None, min_length=3, max_length=3)
    terms: dict | None = None
    metadata: dict | None = None
    status: str | None = Field(None, pattern="^(ACTIVE|EXPIRED|PENDING|CANCELLED)$")
    # Progressive pricing fields
    pricing_model: str | None = Field(None, pattern="^(FIXED|PROGRESSIVE)$")
    progressive_start_date: datetime | None = None
    progressive_month1_pct: float | None = Field(None, ge=0, le=100)
    progressive_month2_pct: float | None = Field(None, ge=0, le=100)


class ContractResponse(BaseModel):
    id: str
    company_id: str
    client_id: str | None
    carrier_id: str
    number: str
    description: str | None
    status: str
    start_date: datetime
    end_date: datetime | None
    success_fee_pct: float
    min_recovery: float | None
    currency: str
    terms: dict | None
    metadata: dict | None
    created_at: datetime
    updated_at: datetime
    tables: list[FreightTableResponse] = []
    # Progressive pricing fields
    pricing_model: str
    progressive_start_date: datetime | None
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
