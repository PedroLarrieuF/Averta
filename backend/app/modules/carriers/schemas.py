"""Carriers module schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class CarrierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    cnpj: str = Field(..., min_length=14, max_length=18)
    state_reg: str | None = Field(None, max_length=20)
    address: dict[str, Any] | None = None
    contact_person: str | None = Field(None, max_length=200)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    bank_info: dict[str, Any] | None = None  # {bank, agency, account, pix}
    settings: dict[str, Any] | None = None


class CarrierUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    state_reg: str | None = Field(None, max_length=20)
    address: dict[str, Any] | None = None
    contact_person: str | None = Field(None, max_length=200)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    bank_info: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    is_active: bool | None = None


class CarrierResponse(BaseModel):
    id: str
    company_id: str
    name: str
    trade_name: str | None
    cnpj: str
    state_reg: str | None
    address: dict[str, Any] | None
    contact_person: str | None
    contact_email: str | None
    contact_phone: str | None
    bank_info: dict[str, Any] | None
    settings: dict[str, Any] | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarrierListResponse(BaseModel):
    items: list[CarrierResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
