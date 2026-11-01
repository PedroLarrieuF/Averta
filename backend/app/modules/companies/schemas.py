"""Companies module schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    cnpj: str = Field(..., min_length=14, max_length=18)
    state_reg: Optional[str] = Field(None, max_length=20)
    municipal_reg: Optional[str] = Field(None, max_length=20)
    address: Optional[dict] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=200)
    settings: Optional[dict] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    state_reg: Optional[str] = Field(None, max_length=20)
    municipal_reg: Optional[str] = Field(None, max_length=20)
    address: Optional[dict] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=200)
    logo_url: Optional[str] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    trade_name: Optional[str]
    cnpj: str
    state_reg: Optional[str]
    municipal_reg: Optional[str]
    address: Optional[dict]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    settings: Optional[dict]
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