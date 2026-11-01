"""Auth module schemas"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=200)
    company_name: str = Field(..., min_length=2, max_length=200)
    company_cnpj: str = Field(..., min_length=14, max_length=18)

    @field_validator("company_cnpj")
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        # Remove non-digits
        digits = "".join(filter(str.isdigit, v))
        if len(digits) != 14:
            raise ValueError("CNPJ must have 14 digits")
        return digits


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


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


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    success: bool
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict