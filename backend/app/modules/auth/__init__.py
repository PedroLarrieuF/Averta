"""Auth module"""

from app.modules.auth.router import router
from app.modules.auth.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService

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
