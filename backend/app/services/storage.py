"""Storage service for S3/MinIO operations"""

import io
from datetime import timedelta

import structlog
from minio import Minio
from minio.error import S3Error

from app.core.config import settings

logger = structlog.get_logger()


class StorageService:
    def __init__(self) -> None:
        self.client = Minio(
            settings.S3_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=settings.S3_ENDPOINT.startswith("https"),
            region=settings.S3_REGION,
        )
        self.bucket = settings.S3_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket, location=settings.S3_REGION)
                logger.info("bucket_created", bucket=self.bucket)
        except S3Error as e:
            logger.error("bucket_error", error=str(e))
            raise

    def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload file to storage"""
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
        """Download file from storage"""
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
        """Delete file from storage"""
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info("file_deleted", object_name=object_name)
            return True
        except S3Error as e:
            logger.error("delete_error", object_name=object_name, error=str(e))
            return False

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """Generate presigned URL for download"""
        try:
            return self.client.presigned_get_object(self.bucket, object_name, expires=timedelta(seconds=expires))
        except S3Error as e:
            logger.error("presigned_url_error", object_name=object_name, error=str(e))
            raise

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists"""
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except S3Error:
            return False


# Global instance
storage_service = StorageService()


# Convenience functions
async def upload_file(
    file_data: bytes, object_name: str, content_type: str = "application/octet-stream"
) -> str:
    return storage_service.upload_file(file_data, object_name, content_type)


async def download_file(bucket: str, object_name: str) -> bytes:
    # For now, use default bucket
    return storage_service.download_file(object_name)


async def get_presigned_url(object_name: str, expires: int = 3600) -> str:
    return storage_service.get_presigned_url(object_name, expires)
