"""Clients module schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    cnpj: str = Field(..., min_length=14, max_length=18)
    state_reg: Optional[str] = Field(None, max_length=20)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[dict] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    settings: Optional[dict] = None  # success_fee_pct, notification_prefs, etc.
    user_id: Optional[str] = None  # Link to user account (client portal)


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    state_reg: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[dict] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class ClientResponse(BaseModel):
    id: str
    company_id: str
    user_id: Optional[str]
    name: str
    trade_name: Optional[str]
    cnpj: str
    state_reg: Optional[str]
    email: str
    phone: Optional[str]
    address: Optional[dict]
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    settings: Optional[dict]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int