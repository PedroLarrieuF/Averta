"""Application configuration using Pydantic Settings with AWS Secrets Manager and Azure Key Vault support"""

import json
import os
import threading
import time
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# =============================================================================
# AWS SECRETS MANAGER CLIENT
# =============================================================================

class AWSSecretsManagerClient:
    """Thread-safe AWS Secrets Manager client with in-memory caching."""

    def __init__(
        self,
        region: str = "us-east-1",
        prefix: str = "averta",
        environment: str = "production",
        cache_ttl: int = 300,
    ):
        self.region = region
        self.prefix = prefix
        self.environment = environment
        self.cache_ttl = cache_ttl
        self._client = None
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
        self._lock = threading.RLock()

    @property
    def client(self):
        """Lazy-initialize the boto3 client."""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    import boto3
                    self._client = boto3.client("secretsmanager", region_name=self.region)
        return self._client

    def _get_secret_name(self, secret_key: str) -> str:
        """Construct the full secret name from the key."""
        return f"{self.prefix}/{self.environment}/{secret_key}"

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached value is still valid."""
        return (time.time() - timestamp) < self.cache_ttl

    def get_secret(self, secret_key: str) -> dict[str, Any] | None:
        """
        Fetch a secret from AWS Secrets Manager with caching.

        Args:
            secret_key: The secret key (e.g., 'database', 'jwt', 'redis')

        Returns:
            Parsed secret value as dict, or None if not found
        """
        secret_name = self._get_secret_name(secret_key)

        # Check cache first
        with self._lock:
            if secret_name in self._cache:
                value, timestamp = self._cache[secret_name]
                if self._is_cache_valid(timestamp):
                    return value

        # Fetch from AWS
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response.get("SecretString")
            if secret_string:
                secret_value: dict[str, Any] = json.loads(secret_string)
                # Update cache
                with self._lock:
                    self._cache[secret_name] = (secret_value, time.time())
                return secret_value
        except Exception:
            # Log error but don't crash - fall back to env vars
            pass

        return None

    def clear_cache(self) -> None:
        """Clear the secrets cache (useful for testing or forced refresh)."""
        with self._lock:
            self._cache.clear()


# =============================================================================
# AZURE KEY VAULT CLIENT
# =============================================================================

class AzureKeyVaultClient:
    """Thread-safe Azure Key Vault client with in-memory caching."""

    def __init__(
        self,
        vault_url: str,
        prefix: str = "averta",
        environment: str = "production",
        cache_ttl: int = 300,
    ):
        self.vault_url = vault_url
        self.prefix = prefix
        self.environment = environment
        self.cache_ttl = cache_ttl
        self._client = None
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
        self._lock = threading.RLock()

    @property
    def client(self):
        """Lazy-initialize the Key Vault client."""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    from azure.identity import DefaultAzureCredential
                    from azure.keyvault.secrets import SecretClient
                    credential = DefaultAzureCredential()
                    self._client = SecretClient(vault_url=self.vault_url, credential=credential)
        return self._client

    def _get_secret_name(self, secret_key: str) -> str:
        """Construct the full secret name from the key."""
        return f"{self.prefix}-{self.environment}-{secret_key}"

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached value is still valid."""
        return (time.time() - timestamp) < self.cache_ttl

    def get_secret(self, secret_key: str) -> dict[str, Any] | None:
        """
        Fetch a secret from Azure Key Vault with caching.

        Args:
            secret_key: The secret key (e.g., 'database', 'jwt', 'redis')

        Returns:
            Parsed secret value as dict, or None if not found
        """
        secret_name = self._get_secret_name(secret_key)

        # Check cache first
        with self._lock:
            if secret_name in self._cache:
                value, timestamp = self._cache[secret_name]
                if self._is_cache_valid(timestamp):
                    return value

        # Fetch from Key Vault
        try:
            from azure.core.exceptions import ResourceNotFoundError
            secret = self.client.get_secret(secret_name)
            if secret.value:
                secret_value: dict[str, Any] = json.loads(secret.value)
                # Update cache
                with self._lock:
                    self._cache[secret_name] = (secret_value, time.time())
                return secret_value
        except ResourceNotFoundError:
            return None
        except json.JSONDecodeError:
            pass
        except Exception:
            # Log error but don't crash - fall back to env vars
            pass

        return None

    def clear_cache(self) -> None:
        """Clear the secrets cache (useful for testing or forced refresh)."""
        with self._lock:
            self._cache.clear()


# =============================================================================
# SECRETS MANAGEMENT
# =============================================================================

# Module-level state for secrets management
_secrets_manager_holder: list[Any] = [None]
_secrets_manager_lock = threading.Lock()
_secrets_loaded_holder: list[bool] = [False]


def _get_secrets_client():
    """Get or create the appropriate secrets client based on environment."""
    if _secrets_manager_holder[0] is None:
        with _secrets_manager_lock:
            if _secrets_manager_holder[0] is None:
                # Check for Azure Key Vault
                if os.getenv("AZURE_KEYVAULT_ENABLED", "false").lower() == "true":
                    vault_url = os.getenv("AZURE_KEYVAULT_URL")
                    if vault_url:
                        _secrets_manager_holder[0] = AzureKeyVaultClient(
                            vault_url=vault_url,
                            prefix=os.getenv("AZURE_KEYVAULT_PREFIX", "averta"),
                            environment=os.getenv("AZURE_KEYVAULT_ENVIRONMENT", "production"),
                            cache_ttl=int(os.getenv("AZURE_KEYVAULT_CACHE_TTL", "300")),
                        )
                        return _secrets_manager_holder[0]

                # Check for AWS Secrets Manager
                if os.getenv("AWS_SECRETS_MANAGER_ENABLED", "false").lower() == "true":
                    _secrets_manager_holder[0] = AWSSecretsManagerClient(
                        region=os.getenv("AWS_REGION", "us-east-1"),
                        prefix=os.getenv("AWS_SECRETS_MANAGER_PREFIX", "averta"),
                        environment=os.getenv("AWS_SECRETS_MANAGER_ENVIRONMENT", "production"),
                        cache_ttl=int(os.getenv("AWS_SECRETS_CACHE_TTL", "300")),
                    )
                    return _secrets_manager_holder[0]

    return _secrets_manager_holder[0]


def load_secrets() -> dict[str, Any]:
    """
    Load all secrets from the configured secrets provider (AWS or Azure).
    This is called once at startup to populate environment variables.
    """
    client = _get_secrets_client()
    if client is None:
        return {}

    secret_keys = ["database", "redis", "storage", "jwt", "sendgrid", "smtp", "app", "minio"]
    all_secrets = {}

    for key in secret_keys:
        secret_value = client.get_secret(key)
        if secret_value:
            all_secrets[key] = secret_value

    return all_secrets


def _apply_database_secrets(secrets: dict[str, Any]) -> None:
    """Apply database secrets to environment variables."""
    # Check for 'database' key (Azure) or 'database' key (AWS)
    db = secrets.get("database")
    if db and all(k in db for k in ("username", "password", "host", "port", "dbname")):
        os.environ[
            "DATABASE_URL"
        ] = f"postgresql://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"
        # Add sslmode=require for Azure PostgreSQL
        if "postgres.database.azure.com" in db.get("host", ""):
            os.environ["DATABASE_URL"] += "?sslmode=require"
    if db and "host" in db and "port" in db:
        os.environ["DATABASE_HOST"] = db["host"]
        os.environ["DATABASE_PORT"] = str(db["port"])


def _apply_redis_secrets(secrets: dict[str, Any]) -> None:
    """Apply Redis secrets to environment variables."""
    redis = secrets.get("redis")
    if redis and "host" in redis and "port" in redis:
        password_part = f":{redis['password']}@" if redis.get("password") else ""
        scheme = "rediss" if redis.get("ssl", False) else "redis"
        # Check if it's Azure Redis (uses rediss:// and port 6380)
        if "redis.cache.windows.net" in redis.get("host", ""):
            scheme = "rediss"
            password_part = f":{redis['password']}@" if redis.get("password") else ""
        os.environ["REDIS_URL"] = f"{scheme}://{password_part}{redis['host']}:{redis['port']}/0"


def _apply_storage_secrets(secrets: dict[str, Any]) -> None:
    """Apply Storage secrets to environment variables (supports both MinIO and Azure)."""
    # Check for Azure storage
    storage = secrets.get("storage")
    if storage and "account_name" in storage:
        os.environ["AZURE_STORAGE_ACCOUNT_NAME"] = storage["account_name"]
        if storage.get("account_key"):
            os.environ["AZURE_STORAGE_ACCOUNT_KEY"] = storage["account_key"]
        if storage.get("endpoint"):
            os.environ["AZURE_STORAGE_ENDPOINT"] = storage["endpoint"]
        if storage.get("container"):
            os.environ["AZURE_STORAGE_CONTAINER_NAME"] = storage["container"]
        return

    # Check for MinIO/S3 storage
    minio = secrets.get("minio") or secrets.get("storage")
    if minio:
        if "access_key" in minio:
            os.environ["S3_ACCESS_KEY"] = minio["access_key"]
        if "secret_key" in minio:
            os.environ["S3_SECRET_KEY"] = minio["secret_key"]
        if "endpoint" in minio:
            os.environ["S3_ENDPOINT"] = minio["endpoint"]
        if "bucket" in minio:
            os.environ["S3_BUCKET"] = minio["bucket"]
        if "region" in minio:
            os.environ["S3_REGION"] = minio["region"]


def _apply_jwt_secrets(secrets: dict[str, Any]) -> None:
    """Apply JWT secrets to environment variables."""
    jwt = secrets.get("jwt")
    if jwt:
        if "secret_key" in jwt:
            os.environ["JWT_SECRET_KEY"] = jwt["secret_key"]
        if "refresh_secret_key" in jwt:
            os.environ["JWT_REFRESH_SECRET_KEY"] = jwt["refresh_secret_key"]
        if "algorithm" in jwt:
            os.environ["JWT_ALGORITHM"] = jwt["algorithm"]


def _apply_sendgrid_secrets(secrets: dict[str, Any]) -> None:
    """Apply SendGrid secrets to environment variables."""
    sg = secrets.get("sendgrid")
    if sg:
        if "api_key" in sg:
            os.environ["SENDGRID_API_KEY"] = sg["api_key"]
        if "from_email" in sg:
            os.environ["SENDGRID_FROM_EMAIL"] = sg["from_email"]
        if "from_name" in sg:
            os.environ["SENDGRID_FROM_NAME"] = sg["from_name"]


def _apply_smtp_secrets(secrets: dict[str, Any]) -> None:
    """Apply SMTP secrets to environment variables."""
    smtp = secrets.get("smtp")
    if smtp:
        if "host" in smtp:
            os.environ["SMTP_HOST"] = smtp["host"]
        if "port" in smtp:
            os.environ["SMTP_PORT"] = str(smtp["port"])
        if "user" in smtp:
            os.environ["SMTP_USER"] = smtp["user"]
        if "password" in smtp:
            os.environ["SMTP_PASSWORD"] = smtp["password"]
        if "from" in smtp:
            os.environ["SMTP_FROM"] = smtp["from"]
        if "tls" in smtp:
            os.environ["SMTP_TLS"] = str(smtp["tls"]).lower()


def _apply_app_secrets(secrets: dict[str, Any]) -> None:
    """Apply app configuration secrets to environment variables."""
    app = secrets.get("app")
    if app:
        if "environment" in app:
            os.environ["ENVIRONMENT"] = app["environment"]
        if "log_level" in app:
            os.environ["LOG_LEVEL"] = app["log_level"]
        if "cors_origins" in app:
            os.environ["CORS_ORIGINS"] = json.dumps(app["cors_origins"])
        if "frontend_url" in app:
            os.environ["FRONTEND_URL"] = app["frontend_url"]
        if "success_fee_percentage" in app:
            os.environ["SUCCESS_FEE_PERCENTAGE"] = str(app["success_fee_percentage"])


def apply_secrets_to_env(secrets: dict[str, dict[str, Any]]) -> None:
    """
    Apply secrets to environment variables for Pydantic to pick up.
    This modifies os.environ so that Settings() reads the secret values.
    """
    _apply_database_secrets(secrets)
    _apply_redis_secrets(secrets)
    _apply_storage_secrets(secrets)
    _apply_jwt_secrets(secrets)
    _apply_sendgrid_secrets(secrets)
    _apply_smtp_secrets(secrets)
    _apply_app_secrets(secrets)


def _load_secrets_once() -> None:
    """Load secrets from configured provider once at startup."""
    if not _secrets_loaded_holder[0]:
        secrets = load_secrets()
        if secrets:
            apply_secrets_to_env(secrets)
        _secrets_loaded_holder[0] = True


# =============================================================================
# SETTINGS
# =============================================================================

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Averta SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/averta"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_CONNECT_TIMEOUT: int = 10
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-min-32-chars", min_length=32
    )
    JWT_REFRESH_SECRET_KEY: str = Field(
        default="dev-refresh-secret-key-change-in-production-min-32-chars", min_length=32
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # S3/MinIO (legacy, for backward compatibility)
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "averta-documents"
    S3_REGION: str = "us-east-1"
    S3_PUBLIC_URL: str = "http://localhost:9000"

    # Azure Blob Storage
    AZURE_STORAGE_ACCOUNT_NAME: str = ""
    AZURE_STORAGE_ACCOUNT_KEY: str = ""
    AZURE_STORAGE_ENDPOINT: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "averta-documents"

    # Azure Key Vault
    AZURE_KEYVAULT_ENABLED: bool = False
    AZURE_KEYVAULT_URL: str = ""
    AZURE_KEYVAULT_PREFIX: str = "averta"
    AZURE_KEYVAULT_ENVIRONMENT: str = "production"
    AZURE_KEYVAULT_CACHE_TTL: int = 300

    # AWS Secrets Manager
    AWS_SECRETS_MANAGER_ENABLED: bool = False
    AWS_REGION: str = "us-east-1"
    AWS_SECRETS_MANAGER_PREFIX: str = "averta"
    AWS_SECRETS_MANAGER_ENVIRONMENT: str = "production"
    AWS_SECRETS_CACHE_TTL: int = 300

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutes

    # Email (optional) - SMTP fallback
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "noreply@averta.com.br"
    SMTP_TLS: bool = True

    # SendGrid
    SENDGRID_API_KEY: str | None = None
    SENDGRID_FROM_EMAIL: str = "noreply@averta.com.br"
    SENDGRID_FROM_NAME: str = "Averta Auditoria"

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:3000"

    # Support email
    SUPPORT_EMAIL: str = "suporte@averta.com.br"

    # Success fee percentage
    SUCCESS_FEE_PERCENTAGE: float = 20.0

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_AUTH_REQUESTS: int = 10
    RATE_LIMIT_UPLOAD_REQUESTS: int = 5
    RATE_LIMIT_API_REQUESTS: int = 100
    RATE_LIMIT_REPORTS_REQUESTS: int = 20
    RATE_LIMIT_DISCREPANCIES_REQUESTS: int = 50
    RATE_LIMIT_CONTESTS_REQUESTS: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # File upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB


@lru_cache
def get_settings() -> Settings:
    # Load secrets from configured provider before creating Settings instance
    _load_secrets_once()
    return Settings()


settings = get_settings()