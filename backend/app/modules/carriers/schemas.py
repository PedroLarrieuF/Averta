"""Carriers module schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CarrierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    cnpj: str = Field(..., min_length=14, max_length=18)
    state_reg: Optional[str] = Field(None, max_length=20)
    address: Optional[dict] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    bank_info: Optional[dict] = None  # {bank, agency, account, pix}
    settings: Optional[dict] = None


class CarrierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    state_reg: Optional[str] = Field(None, max_length=20)
    address: Optional[dict] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    bank_info: Optional[dict] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class CarrierResponse(BaseModel):
    id: str
    company_id: str
    name: str
    trade_name: Optional[str]
    cnpj: str
    state_reg: Optional[str]
    address: Optional[dict]
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    bank_info: Optional[dict]
    settings: Optional[dict]
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