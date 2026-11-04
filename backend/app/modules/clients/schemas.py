"""Clients module schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    cnpj: str = Field(..., min_length=14, max_length=18)
    state_reg: str | None = Field(None, max_length=20)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    address: dict[str, Any] | None = None
    contact_person: str | None = Field(None, max_length=200)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    settings: dict[str, Any] | None = None  # success_fee_pct, notification_prefs, etc.
    user_id: str | None = None  # Link to user account (client portal)


class ClientUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    state_reg: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: dict[str, Any] | None = None
    contact_person: str | None = Field(None, max_length=200)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    settings: dict[str, Any] | None = None
    is_active: bool | None = None


class ClientResponse(BaseModel):
    id: str
    company_id: str
    user_id: str | None
    name: str
    trade_name: str | None
    cnpj: str
    state_reg: str | None
    email: str
    phone: str | None
    address: dict[str, Any] | None
    contact_person: str | None
    contact_email: str | None
    contact_phone: str | None
    settings: dict[str, Any] | None
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
