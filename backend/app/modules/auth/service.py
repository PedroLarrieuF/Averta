"""Auth service: authentication, registration, token management"""

from datetime import UTC, datetime
from typing import Any

import structlog

from app.core.config import settings
from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.security import (
    create_password_reset_token,
    create_tokens,
    decode_refresh_token,
    get_password_hash,
    verify_password,
    verify_password_reset_token,
)
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from prisma import Prisma

logger = structlog.get_logger()


class AuthService:
    def __init__(self, db: Prisma):
        self.db = db

    async def login(self, data: LoginRequest) -> AuthResponse:
        """Authenticate user and return tokens"""
        user = await self.db.user.find_unique(
            where={"email": data.email},
            include={"company": True, "client": True},
        )

        if not user or not user.passwordHash:
            logger.warning("login_failed_user_not_found", email=data.email)
            raise UnauthorizedError("Invalid credentials")

        if user.status != "ACTIVE":
            logger.warning("login_failed_user_inactive", email=data.email, status=user.status)
            raise UnauthorizedError("Account is not active")

        if not verify_password(data.password, user.passwordHash):
            logger.warning("login_failed_invalid_password", email=data.email)
            raise UnauthorizedError("Invalid credentials")

        # Update last login
        await self.db.user.update(
            where={"id": user.id},
            data={"lastLoginAt": datetime.now(UTC)},
        )

        tokens = create_tokens(
            subject=user.id,
            email=user.email,
            role=user.role,
            company_id=user.companyId,
            client_id=user.clientId,
        )

        logger.info("login_success", user_id=user.id, email=user.email)

        return AuthResponse(
            user=self._to_user_response(user),
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
        )

    async def register(self, data: RegisterRequest) -> AuthResponse:
        """Register new company and admin user"""
        # Check email uniqueness
        existing_user = await self.db.user.find_unique(where={"email": data.email})
        if existing_user:
            raise ConflictError("Email already registered", {"field": "email"})

        # Check CNPJ uniqueness
        existing_company = await self.db.company.find_unique(where={"cnpj": data.company_cnpj})
        if existing_company:
            raise ConflictError("Company CNPJ already registered", {"field": "company_cnpj"})

        # Hash password
        password_hash = get_password_hash(data.password)

        # Create company and user in transaction
        async with self.db.tx() as tx:
            company = await tx.company.create(
                data={
                    "name": data.company_name,
                    "cnpj": data.company_cnpj,
                    "email": data.email,
                }
            )

            user = await tx.user.create(
                data={
                    "email": data.email,
                    "passwordHash": password_hash,
                    "fullName": data.full_name,
                    "role": "ADMIN",
                    "status": "ACTIVE",
                    "companyId": company.id,
                }
            )

        tokens = create_tokens(
            subject=user.id,
            email=user.email,
            role=user.role,
            company_id=user.companyId,
        )

        logger.info("registration_success", user_id=user.id, company_id=company.id)

        # Fetch with relations for response
        user_with_relations = await self.db.user.find_unique(
            where={"id": user.id},
            include={"company": True, "client": True},
        )

        return AuthResponse(
            user=self._to_user_response(user_with_relations),
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise UnauthorizedError("Invalid or expired refresh token")

        user = await self.db.user.find_unique(where={"id": payload.sub})
        if not user or user.status != "ACTIVE":
            raise UnauthorizedError("User not found or inactive")

        tokens = create_tokens(
            subject=user.id,
            email=user.email,
            role=user.role,
            company_id=user.companyId,
            client_id=user.clientId,
        )

        logger.info("token_refreshed", user_id=user.id)
        return TokenResponse(**tokens.model_dump())

    async def logout(self, user_id: str) -> None:
        """Logout - in stateless JWT, client just discards tokens.
        Could implement token blacklist here if needed."""
        logger.info("logout", user_id=user_id)

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        """Change user password"""
        user = await self.db.user.find_unique(where={"id": user_id})
        if not user or not user.passwordHash:
            raise NotFoundError("User", user_id)

        if not verify_password(current_password, user.passwordHash):
            raise BadRequestError("Current password is incorrect")

        new_hash = get_password_hash(new_password)
        await self.db.user.update(
            where={"id": user_id},
            data={"passwordHash": new_hash},
        )

        logger.info("password_changed", user_id=user_id)

    async def request_password_reset(self, email: str) -> None:
        """Request password reset - sends token via email (logged in dev)"""
        user = await self.db.user.find_unique(where={"email": email})
        if not user:
            # Don't reveal if email exists
            logger.info("password_reset_requested_unknown_email", email=email)
            return

        reset_token = create_password_reset_token(email)

        # In production, send email with reset link
        # For dev, log it
        if settings.ENVIRONMENT != "production":
            logger.info(
                "password_reset_token",
                email=email,
                token=reset_token,
                reset_url=f"{settings.FRONTEND_URL}/reset-password?token={reset_token}",
            )

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset password with token"""
        email = verify_password_reset_token(token)
        if not email:
            raise BadRequestError("Invalid or expired reset token")

        user = await self.db.user.find_unique(where={"email": email})
        if not user:
            raise BadRequestError("Invalid or expired reset token")

        new_hash = get_password_hash(new_password)
        await self.db.user.update(
            where={"id": user.id},
            data={"passwordHash": new_hash},
        )

        logger.info("password_reset_completed", user_id=user.id)

    async def get_profile(self, user_id: str) -> UserResponse:
        """Get current user profile"""
        user = await self.db.user.find_unique(
            where={"id": user_id},
            include={"company": True, "client": True},
        )
        if not user:
            raise NotFoundError("User", user_id)
        return self._to_user_response(user)

    def _to_user_response(self, user: Any) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.fullName,
            role=user.role,
            status=user.status,
            company_id=user.companyId,
            client_id=user.clientId,
            avatar_url=user.avatarUrl,
            last_login_at=user.lastLoginAt,
            created_at=user.createdAt,
        )
