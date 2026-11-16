"""Storage service for Azure Blob Storage operations"""

import io
from datetime import timedelta
from threading import Lock
from typing import Optional

import structlog
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions

from app.core.config import settings

logger = structlog.get_logger()


class AzureBlobStorageService:
    """Azure Blob Storage service for document storage."""

    def __init__(self) -> None:
        self.credential = DefaultAzureCredential()
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self.endpoint = settings.AZURE_STORAGE_ENDPOINT
        self._blob_service_client: Optional[BlobServiceClient] = None
        self._container_client: Optional[ContainerClient] = None
        self._container_ensured = False
        self._container_lock = Lock()

    @property
    def blob_service_client(self) -> BlobServiceClient:
        """Get or create blob service client."""
        if self._blob_service_client is None:
            if self.account_key:
                # Use account key for authentication
                self._blob_service_client = BlobServiceClient(
                    account_url=self.endpoint,
                    credential=self.account_key
                )
            else:
                # Use managed identity / DefaultAzureCredential
                self._blob_service_client = BlobServiceClient(
                    account_url=self.endpoint,
                    credential=self.credential
                )
        return self._blob_service_client

    @property
    def container_client(self) -> ContainerClient:
        """Get or create container client."""
        if self._container_client is None:
            self._container_client = self.blob_service_client.get_container_client(self.container_name)
        return self._container_client

    def _ensure_container(self) -> None:
        """Create container if it doesn't exist (thread-safe, idempotent)."""
        if self._container_ensured:
            return
        with self._container_lock:
            if self._container_ensured:
                return
            try:
                if not self.container_client.exists():
                    self.container_client.create_container()
                    logger.info("container_created", container=self.container_name)
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
        """Upload file to Azure Blob Storage."""
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
        """Upload file stream to Azure Blob Storage."""
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
        """Download file from Azure Blob Storage."""
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
        """Download file as stream from Azure Blob Storage."""
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
        """Delete file from Azure Blob Storage."""
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
        permission: BlobSasPermissions = BlobSasPermissions(read=True)
    ) -> str:
        """Generate SAS URL for blob access."""
        self._ensure_container()
        try:
            if not self.account_key:
                # If using managed identity, generate user delegation SAS
                # This requires additional setup, fallback to account key for now
                raise ValueError("Account key required for SAS generation with managed identity")

            blob_client = self.container_client.get_blob_client(object_name)
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=object_name,
                account_key=self.account_key,
                permission=permission,
                expiry=timedelta(seconds=expires)
            )

            url = f"{blob_client.url}?{sas_token}"
            logger.info("presigned_url_generated", object_name=object_name, expires=expires)
            return url
        except Exception as e:
            logger.error("presigned_url_error", object_name=object_name, error=str(e))
            raise

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in Azure Blob Storage."""
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            return blob_client.exists()
        except HttpResponseError:
            return False

    def get_file_metadata(self, object_name: str) -> Optional[dict]:
        """Get file metadata."""
        self._ensure_container()
        try:
            blob_client = self.container_client.get_blob_client(object_name)
            props = blob_client.get_blob_properties()
            return {
                "size": props.size,
                "content_type": props.content_settings.content_type,
                "last_modified": props.last_modified,
                "metadata": props.metadata,
                "etag": props.etag
            }
        except ResourceNotFoundError:
            return None
        except HttpResponseError as e:
            logger.error("metadata_error", object_name=object_name, error=str(e))
            return None

    def list_files(self, prefix: str = "", max_results: int = 1000) -> list[dict]:
        """List files in container with optional prefix."""
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


# Lazy-initialized global instance
_storage_service: Optional[AzureBlobStorageService] = None
_storage_lock = Lock()


def get_storage_service() -> AzureBlobStorageService:
    """Get or create the global storage service instance (lazy initialization)."""
    global _storage_service
    if _storage_service is None:
        with _storage_lock:
            if _storage_service is None:
                _storage_service = AzureBlobStorageService()
    return _storage_service


# Convenience functions (lazy initialization)
async def upload_file(
    file_data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
    metadata: Optional[dict] = None
) -> str:
    return get_storage_service().upload_file(file_data, object_name, content_type, metadata)


async def upload_file_stream(
    file_stream: io.IOBase,
    object_name: str,
    content_type: str = "application/octet-stream",
    metadata: Optional[dict] = None
) -> str:
    return get_storage_service().upload_file_stream(file_stream, object_name, content_type, metadata)


async def download_file(object_name: str) -> bytes:
    return get_storage_service().download_file(object_name)


async def download_file_stream(object_name: str) -> io.BytesIO:
    return get_storage_service().download_file_stream(object_name)


async def delete_file(object_name: str) -> bool:
    return get_storage_service().delete_file(object_name)


async def get_presigned_url(object_name: str, expires: int = 3600) -> str:
    return get_storage_service().get_presigned_url(object_name, expires)


async def file_exists(object_name: str) -> bool:
    return get_storage_service().file_exists(object_name)


async def get_file_metadata(object_name: str) -> Optional[dict]:
    return get_storage_service().get_file_metadata(object_name)