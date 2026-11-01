"""Users module schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.core.exceptions import AppException
from app.modules.base import BaseService


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    role: str = Field(..., pattern="^(ADMIN|AUDITOR|MANAGER|CLIENT)$")
    client_id: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    role: Optional[str] = Field(None, pattern="^(ADMIN|AUDITOR|MANAGER|CLIENT)$")
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|PENDING|BLOCKED)$")
    client_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    status: str
    company_id: str
    client_id: Optional[str] = None
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int