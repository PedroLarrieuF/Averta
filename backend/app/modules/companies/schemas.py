"""Companies module schemas"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    cnpj: str = Field(..., min_length=14, max_length=18)
    state_reg: str | None = Field(None, max_length=20)
    municipal_reg: str | None = Field(None, max_length=20)
    address: dict | None = None
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    website: str | None = Field(None, max_length=200)
    settings: dict | None = None


class CompanyUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    state_reg: str | None = Field(None, max_length=20)
    municipal_reg: str | None = Field(None, max_length=20)
    address: dict | None = None
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    website: str | None = Field(None, max_length=200)
    logo_url: str | None = None
    settings: dict | None = None
    is_active: bool | None = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    trade_name: str | None
    cnpj: str
    state_reg: str | None
    municipal_reg: str | None
    address: dict | None
    phone: str | None
    email: str | None
    website: str | None
    logo_url: str | None
    settings: dict | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
