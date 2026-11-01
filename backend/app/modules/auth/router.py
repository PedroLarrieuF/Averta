"""Auth module router"""
from fastapi import APIRouter, Depends, status
from prisma import Prisma

from app.core.dependencies import (
    get_database,
    CurrentUserDep,
    RateLimitDep,
)
from app.core.exceptions import UnauthorizedError
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthResponse,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: Prisma = Depends(get_database)) -> AuthService:
    return AuthService(db)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    dependencies=[RateLimitDep],
)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate user with email and password"""
    return await auth_service.login(data)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new company and admin user",
    dependencies=[RateLimitDep],
)
async def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new company with an admin user"""
    return await auth_service.register(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    dependencies=[RateLimitDep],
)
async def refresh(
    data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get new access token using refresh token"""
    return await auth_service.refresh(data.refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
)
async def logout(
    current_user: CurrentUserDep,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Logout - client should discard tokens"""
    await auth_service.logout(current_user.sub)
    return MessageResponse(success=True, message="Logged out successfully")


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUserDep,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Change current user's password"""
    await auth_service.change_password(current_user.sub, data.current_password, data.new_password)
    return MessageResponse(success=True, message="Password changed successfully")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    dependencies=[RateLimitDep],
)
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request password reset link via email"""
    await auth_service.request_password_reset(data.email)
    return MessageResponse(
        success=True,
        message="If the email exists, a reset link has been sent",
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password with token",
    dependencies=[RateLimitDep],
)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Reset password using token from email"""
    await auth_service.reset_password(data.token, data.new_password)
    return MessageResponse(success=True, message="Password reset successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_profile(
    current_user: CurrentUserDep,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get authenticated user's profile"""
    return await auth_service.get_profile(current_user.sub)