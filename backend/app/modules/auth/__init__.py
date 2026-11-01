"""Auth module"""
from app.modules.auth.router import router
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    MessageResponse,
)

__all__ = [
    "router",
    "AuthService",
    "LoginRequest",
    "RegisterRequest",
    "RefreshRequest",
    "ChangePasswordRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "TokenResponse",
    "UserResponse",
    "AuthResponse",
    "MessageResponse",
]