"""Users module schemas"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    role: str = Field(..., pattern="^(ADMIN|AUDITOR|MANAGER|CLIENT)$")
    client_id: str | None = None
    password: str | None = Field(None, min_length=8, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=200)
    role: str | None = Field(None, pattern="^(ADMIN|AUDITOR|MANAGER|CLIENT)$")
    status: str | None = Field(None, pattern="^(ACTIVE|INACTIVE|PENDING|BLOCKED)$")
    client_id: str | None = None
    avatar_url: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    status: str
    company_id: str
    client_id: str | None = None
    avatar_url: str | None = None
    last_login_at: datetime | None = None
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
