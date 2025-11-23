from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError
import cloudinary
import cloudinary.uploader
from app.core.config import settings
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """Abstract base class for file storage services"""

    @abstractmethod
    def upload(
        self,
        file: BinaryIO,
        file_name: str,
        folder: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file and return the URL"""
        pass

    @abstractmethod
    def delete(self, file_url: str) -> bool:
        """Delete a file"""
        pass

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """Get the public URL for a file"""
        pass


class S3StorageService(StorageService):
    """AWS S3 storage service implementation"""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET

    def upload(
        self,
        file: BinaryIO,
        file_name: str,
        folder: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to S3"""
        try:
            # Construct S3 key
            if folder:
                s3_key = f"{folder}/{file_name}"
            else:
                s3_key = file_name

            # Upload file
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                extra_args['ACL'] = 'public-read'

            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            # Get the URL
            url = self.get_url(s3_key)

            logger.info(f"File uploaded successfully to S3: {url}")
            return url

        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise

    def delete(self, file_url: str) -> bool:
        """Delete a file from S3"""
        try:
            # Extract S3 key from URL
            s3_key = self._extract_key_from_url(file_url)

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )

            logger.info(f"File deleted successfully from S3: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            return False

    def get_url(self, file_path: str) -> str:
        """Get the public URL for a file in S3"""
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_path}"

    def _extract_key_from_url(self, url: str) -> str:
        """Extract S3 key from URL"""
        # Remove the base URL part
        base_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/"
        return url.replace(base_url, "")

    def generate_presigned_url(self, file_path: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for temporary access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise


class CloudinaryStorageService(StorageService):
    """Cloudinary storage service implementation"""

    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )

    def upload(
        self,
        file: BinaryIO,
        file_name: str,
        folder: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to Cloudinary"""
        try:
            # Determine resource type based on content type
            resource_type = "auto"
            if content_type:
                if content_type.startswith("image/"):
                    resource_type = "image"
                elif content_type.startswith("video/"):
                    resource_type = "video"

            # Upload options
            upload_options = {
                "resource_type": resource_type,
                "use_filename": True,
                "unique_filename": True,
                "overwrite": False
            }

            if folder:
                upload_options["folder"] = folder

            # Upload file
            result = cloudinary.uploader.upload(file, **upload_options)

            logger.info(f"File uploaded successfully to Cloudinary: {result['secure_url']}")
            return result['secure_url']

        except Exception as e:
            logger.error(f"Error uploading file to Cloudinary: {str(e)}")
            raise

    def delete(self, file_url: str) -> bool:
        """Delete a file from Cloudinary"""
        try:
            # Extract public_id from URL
            public_id = self._extract_public_id_from_url(file_url)

            # Delete file
            result = cloudinary.uploader.destroy(public_id)

            if result.get('result') == 'ok':
                logger.info(f"File deleted successfully from Cloudinary: {public_id}")
                return True
            else:
                logger.error(f"Failed to delete file from Cloudinary: {public_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting file from Cloudinary: {str(e)}")
            return False

    def get_url(self, file_path: str) -> str:
        """Get the public URL for a file in Cloudinary"""
        # Cloudinary URLs are already public URLs
        return file_path

    def _extract_public_id_from_url(self, url: str) -> str:
        """Extract public_id from Cloudinary URL"""
        # Example: https://res.cloudinary.com/demo/image/upload/v1234567890/folder/filename.jpg
        # Public ID: folder/filename
        parts = url.split('/')
        # Find the upload index
        if 'upload' in parts:
            upload_index = parts.index('upload')
            # Get parts after version (v1234567890)
            public_id_parts = parts[upload_index + 2:]
            # Remove file extension
            public_id = '/'.join(public_id_parts)
            return Path(public_id).stem
        return url

    def transform_image(
        self,
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        crop: str = "fill",
        quality: str = "auto"
    ) -> str:
        """Generate a transformed image URL"""
        transformation_options = {
            "quality": quality,
            "crop": crop
        }

        if width:
            transformation_options["width"] = width
        if height:
            transformation_options["height"] = height

        url = cloudinary.CloudinaryImage(public_id).build_url(**transformation_options)
        return url


class StorageFactory:
    """Factory to create storage service instances"""

    @staticmethod
    def get_storage(storage_type: str = "s3") -> StorageService:
        """Get storage service instance"""
        if storage_type.lower() == "s3":
            return S3StorageService()
        elif storage_type.lower() == "cloudinary":
            return CloudinaryStorageService()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")


# Convenience function
def get_default_storage() -> StorageService:
    """Get the default storage service based on configuration"""
    # Default to S3, but can be configured
    return StorageFactory.get_storage("s3")
