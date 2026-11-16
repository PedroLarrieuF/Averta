"""Unified storage service supporting both MinIO (S3-compatible) and Azure Blob Storage"""

import io
import os
from datetime import timedelta
from threading import Lock
from typing import Optional

import structlog
from pydantic import BaseModel

from app.core.config import settings

logger = structlog.get_logger()


class StorageConfig(BaseModel):
    """Storage configuration"""
    provider: str = "minio"  # "minio" or "azure"

    # MinIO/S3 settings
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "averta-documents"
    s3_region: str = "us-east-1"
    s3_public_url: str = "http://localhost:9000"

    # Azure Blob Storage settings
    azure_account_name: str = ""
    azure_account_key: str = ""
    azure_endpoint: str = ""
    azure_container: str = "averta-documents"


def get_storage_config() -> StorageConfig:
    """Get storage configuration from settings."""
    # Check for Azure storage configuration
    if settings.AZURE_STORAGE_ACCOUNT_NAME and settings.AZURE_STORAGE_ENDPOINT:
        return StorageConfig(
            provider="azure",
            azure_account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
            azure_account_key=settings.AZURE_STORAGE_ACCOUNT_KEY or "",
            azure_endpoint=settings.AZURE_STORAGE_ENDPOINT,
            azure_container=settings.AZURE_STORAGE_CONTAINER_NAME,
        )

    # Default to MinIO/S3
    return StorageConfig(
        provider="minio",
        s3_endpoint=settings.S3_ENDPOINT,
        s3_access_key=settings.S3_ACCESS_KEY,
        s3_secret_key=settings.S3_SECRET_KEY,
        s3_bucket=settings.S3_BUCKET,
        s3_region=settings.S3_REGION,
        s3_public_url=settings.S3_PUBLIC_URL,
    )


# =============================================================================
# MINIO STORAGE SERVICE
# =============================================================================

class MinioStorageService:
    """MinIO/S3-compatible storage service."""

    def __init__(self, config: StorageConfig) -> None:
        from minio import Minio
        from minio.error import S3Error

        self.config = config
        self.client = Minio(
            config.s3_endpoint.replace("http://", "").replace("https://", ""),
            access_key=config.s3_access_key,
            secret_key=config.s3_secret_key,
            secure=config.s3_endpoint.startswith("https"),
            region=config.s3_region,
        )
        self.bucket = config.s3_bucket
        self._bucket_ensured = False
        self._bucket_lock = Lock()

    def _ensure_bucket(self) -> None:
        from minio.error import S3Error
        if self._bucket_ensured:
            return
        with self._bucket_lock:
            if self._bucket_ensured:
                return
            try:
                if not self.client.bucket_exists(self.bucket):
                    self.client.make_bucket(self.bucket, location=self.config.s3_region)
                    logger.info("bucket_created", bucket=self.bucket)
                self._bucket_ensured = True
            except S3Error as e:
                logger.error("bucket_error", error=str(e))
                raise

    def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        self._ensure_bucket()
        from minio.error import S3Error
        try:
            self.client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            logger.info("file_uploaded", object_name=object_name, size=len(file_data))
            return object_name
        except S3Error as e:
            logger.error("upload_error", object_name=object_name, error=str(e))
            raise

    def download_file(self, object_name: str) -> bytes:
        self._ensure_bucket()
        from minio.error import S3Error
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error("download_error", object_name=object_name, error=str(e))
            raise

    def delete_file(self, object_name: str) -> bool:
        self._ensure_bucket()
        from minio.error import S3Error
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info("file_deleted", object_name=object_name)
            return True
        except S3Error as e:
            logger.error("delete_error", object_name=object_name, error=str(e))
            return False

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        self._ensure_bucket()
        from minio.error import S3Error
        try:
            return self.client.presigned_get_object(
                self.bucket, object_name, expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            logger.error("presigned_url_error", object_name=object_name, error=str(e))
            raise

    def file_exists(self, object_name: str) -> bool:
        self._ensure_bucket()
        from minio.error import S3Error
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except S3Error:
            return False

    def get_file_metadata(self, object_name: str) -> Optional[dict]:
        self._ensure_bucket()
        from minio.error import S3Error
        try:
            stat = self.client.stat_object(self.bucket, object_name)
            return {
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata,
                "etag": stat.etag,
            }
        except S3Error:
            return None


# =============================================================================
# AZURE BLOB STORAGE SERVICE
# =============================================================================

class AzureBlobStorageService:
    """Azure Blob Storage service."""

    def __init__(self, config: StorageConfig) -> None:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        self.config = config
        self.credential = DefaultAzureCredential()
        self._blob_service_client = None
        self._container_client = None
        self._container_ensured = False
        self._container_lock = Lock()

    @property
    def blob_service_client(self):
        from azure.storage.blob import BlobServiceClient
        if self._blob_service_client is None:
            if self.config.azure_account_key:
                self._blob_service_client = BlobServiceClient(
                    account_url=self.config.azure_endpoint,
                    credential=self.config.azure_account_key
                )
            else:
                self._blob_service_client = BlobServiceClient(
                    account_url=self.config.azure_endpoint,
                    credential=self.credential
                )
        return self._blob_service_client

    @property
    def container_client(self):
        from azure.storage.blob import ContainerClient
        if self._container_client is None:
            self._container_client = self.blob_service_client.get_container_client(self.config.azure_container)
        return self._container_client

    def _ensure_container(self) -> None:
        from azure.core.exceptions import HttpResponseError
        if self._container_ensured:
            return
        with self._container_lock:
            if self._container_ensured:
                return
            try:
                if not self.container_client.exists():
                    self.container_client.create_container()
                    logger.info("container_created", container=self.config.azure_container)
                self._container_ensured = True
            except HttpResponseError as e:
                logger.error("container_error", error=str(e))
                raise

    def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> str:
        from azure.core.exceptions import HttpResponseError
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            blob_client.upload_blob(
                file_data,
                overwrite=True,
                content_type=content_type,
                metadata=metadata or {}
            )
            logger.info("file_uploaded", object_name=object_name, size=len(file_data))
            return object_name
        except HttpResponseError as e:
            logger.error("upload_error", object_name=object_name, error=str(e))
            raise

    def upload_file_stream(
        self,
        file_stream: io.IOBase,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> str:
        from azure.core.exceptions import HttpResponseError
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            blob_client.upload_blob(
                file_stream,
                overwrite=True,
                content_type=content_type,
                metadata=metadata or {}
            )
            logger.info("file_uploaded", object_name=object_name)
            return object_name
        except HttpResponseError as e:
            logger.error("upload_error", object_name=object_name, error=str(e))
            raise

    def download_file(self, object_name: str) -> bytes:
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            if not blob_client.exists():
                raise ResourceNotFoundError(f"Blob not found: {object_name}")

            stream = blob_client.download_blob()
            data = stream.readall()
            logger.info("file_downloaded", object_name=object_name, size=len(data))
            return data
        except ResourceNotFoundError:
            logger.error("download_error", object_name=object_name, error="Blob not found")
            raise
        except HttpResponseError as e:
            logger.error("download_error", object_name=object_name, error=str(e))
            raise

    def download_file_stream(self, object_name: str) -> io.BytesIO:
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            if not blob_client.exists():
                raise ResourceNotFoundError(f"Blob not found: {object_name}")

            stream = blob_client.download_blob()
            data = io.BytesIO(stream.readall())
            data.seek(0)
            return data
        except ResourceNotFoundError:
            logger.error("download_error", object_name=object_name, error="Blob not found")
            raise
        except HttpResponseError as e:
            logger.error("download_error", object_name=object_name, error=str(e))
            raise

    def delete_file(self, object_name: str) -> bool:
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            blob_client.delete_blob()
            logger.info("file_deleted", object_name=object_name)
            return True
        except ResourceNotFoundError:
            logger.warning("delete_error", object_name=object_name, error="Blob not found")
            return False
        except HttpResponseError as e:
            logger.error("delete_error", object_name=object_name, error=str(e))
            return False

    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from azure.core.exceptions import HttpResponseError
        self._ensure_container()
        try:
            if not self.config.azure_account_key:
                raise ValueError("Account key required for SAS generation")

            blob_client = self.container_client.get_blob_client(object_name)
            sas_token = generate_blob_sas(
                account_name=self.config.azure_account_name,
                container_name=self.config.azure_container,
                blob_name=object_name,
                account_key=self.config.azure_account_key,
                permission=BlobSasPermissions(read=True),
                expiry=timedelta(seconds=expires)
            )

            url = f"{blob_client.url}?{sas_token}"
            logger.info("presigned_url_generated", object_name=object_name, expires=expires)
            return url
        except Exception as e:
            logger.error("presigned_url_error", object_name=object_name, error=str(e))
            raise

    def file_exists(self, object_name: str) -> bool:
        from azure.core.exceptions import HttpResponseError
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            return blob_client.exists()
        except HttpResponseError:
            return False

    def get_file_metadata(self, object_name: str) -> Optional[dict]:
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            props = blob_client.get_blob_properties()
            return {
                "size": props.size,
                "content_type": props.content_settings.content_type,
                "last_modified": props.last_modified,
                "metadata": props.metadata,
                "etag": props.etag,
            }
        except ResourceNotFoundError:
            return None
        except HttpResponseError as e:
            logger.error("metadata_error", object_name=object_name, error=str(e))
            return None

    def list_files(self, prefix: str = "", max_results: int = 1000) -> list[dict]:
        from azure.core.exceptions import HttpResponseError
        self._ensure_container()
        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix, max_results=max_results)
            return [
                {
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified,
                    "content_type": blob.content_settings.content_type,
                }
                for blob in blobs
            ]
        except HttpResponseError as e:
            logger.error("list_error", prefix=prefix, error=str(e))
            return []


# =============================================================================
# STORAGE FACTORY
# =============================================================================

_storage_service = None
_storage_lock = Lock()


def _get_storage_service():
    """Get or create the appropriate storage service based on configuration."""
    global _storage_service
    if _storage_service is None:
        with _storage_lock:
            if _storage_service is None:
                config = get_storage_config()
                if config.provider == "azure":
                    _storage_service = AzureBlobStorageService(config)
                else:
                    _storage_service = MinioStorageService(config)
    return _storage_service


# =============================================================================
# CONVENIENCE FUNCTIONS (Backward Compatible)
# =============================================================================

async def upload_file(
    file_data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
    metadata: Optional[dict] = None,
) -> str:
    """Upload file to storage (MinIO or Azure Blob Storage)."""
    service = _get_storage_service()
    if isinstance(service, AzureBlobStorageService):
        return service.upload_file(file_data, object_name, content_type, metadata)
    return service.upload_file(file_data, object_name, content_type)


async def upload_file_stream(
    file_stream: io.IOBase,
    object_name: str,
    content_type: str = "application/octet-stream",
    metadata: Optional[dict] = None,
) -> str:
    """Upload file stream to storage (Azure Blob Storage only)."""
    service = _get_storage_service()
    if isinstance(service, AzureBlobStorageService):
        return service.upload_file_stream(file_stream, object_name, content_type, metadata)
    # For MinIO, read stream and upload as bytes
    file_data = file_stream.read()
    return await upload_file(file_data, object_name, content_type, metadata)


async def download_file(object_name: str) -> bytes:
    """Download file from storage."""
    service = _get_storage_service()
    return service.download_file(object_name)


async def download_file_stream(object_name: str) -> io.BytesIO:
    """Download file as stream from storage (Azure Blob Storage only)."""
    service = _get_storage_service()
    if isinstance(service, AzureBlobStorageService):
        return service.download_file_stream(object_name)
    # For MinIO, download as bytes and wrap in BytesIO
    data = await download_file(object_name)
    return io.BytesIO(data)


async def delete_file(object_name: str) -> bool:
    """Delete file from storage."""
    service = _get_storage_service()
    return service.delete_file(object_name)


async def get_presigned_url(object_name: str, expires: int = 3600) -> str:
    """Generate presigned URL for file access."""
    service = _get_storage_service()
    return service.get_presigned_url(object_name, expires)


async def file_exists(object_name: str) -> bool:
    """Check if file exists in storage."""
    service = _get_storage_service()
    return service.file_exists(object_name)


async def get_file_metadata(object_name: str) -> Optional[dict]:
    """Get file metadata."""
    service = _get_storage_service()
    return service.get_file_metadata(object_name)