"""Security utilities: JWT, password hashing, token management"""

from datetime import UTC, datetime, timedelta

import structlog
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

logger = structlog.get_logger()

# Password hashing
# Use bcrypt_sha256 for new passwords (supports > 72 bytes via internal SHA-256 pre-hashing)
# Fall back to bcrypt for backward compatibility with existing hashes
# This handles the bcrypt 72-byte limit and provides seamless migration
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    company_id: str
    client_id: str | None = None
    exp: int
    iat: int
    type: str = "access"


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash.

    Supports both new bcrypt-sha256 hashes (for passwords > 72 bytes)
    and legacy bcrypt hashes (for backward compatibility).
    """
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore[no-any-return]


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt-sha256 (supports passwords longer than 72 bytes)."""
    return pwd_context.hash(password)  # type: ignore[no-any-return]


def create_access_token(  # noqa: PLR0913, PLR0917
    subject: str,
    email: str,
    role: str,
    company_id: str,
    client_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create JWT access token"""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": subject,
        "email": email,
        "role": role,
        "company_id": company_id,
        "client_id": client_id,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt  # type: ignore[no-any-return]


def create_refresh_token(
    subject: str,
    email: str,
    role: str,
    company_id: str,
    client_id: str | None = None,
) -> str:
    """Create JWT refresh token"""
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": subject,
        "email": email,
        "role": role,
        "company_id": company_id,
        "client_id": client_id,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt  # type: ignore[no-any-return]


def create_tokens(
    subject: str,
    email: str,
    role: str,
    company_id: str,
    client_id: str | None = None,
) -> TokenData:
    """Create both access and refresh tokens"""
    access_token = create_access_token(subject, email, role, company_id, client_id)
    refresh_token = create_refresh_token(subject, email, role, company_id, client_id)
    return TokenData(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def decode_access_token(token: str) -> TokenPayload | None:
    """Decode and validate access token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return TokenPayload(**payload)
    except JWTError as e:
        logger.warning("invalid_access_token", error=str(e))
        return None


def decode_refresh_token(token: str) -> TokenPayload | None:
    """Decode and validate refresh token"""
    try:
        payload = jwt.decode(
            token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return None
        return TokenPayload(**payload)
    except JWTError as e:
        logger.warning("invalid_refresh_token", error=str(e))
        return None


def create_password_reset_token(email: str) -> str:
    """Create password reset token (1 hour expiry)"""
    now = datetime.now(UTC)
    expire = now + timedelta(hours=1)
    to_encode = {
        "sub": email,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "password_reset",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)  # type: ignore[no-any-return]


def verify_password_reset_token(token: str) -> str | None:
    """Verify password reset token and return email"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")  # type: ignore[no-any-return]
    except JWTError:
        return None
