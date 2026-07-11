from datetime import timedelta
from minio import Minio
from app.config.settings import settings

class FileService:
    bucket = settings.s3_bucket
    client = Minio(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=settings.s3_secure,
    )

    @classmethod
    def sign_upload(cls, key: str, expires_s: int = 60):
        return cls.client.presigned_put_object(
            bucket_name=cls.bucket,
            object_name=key,
            expires=timedelta(seconds=expires_s)
        )

    @classmethod
    def sign_download(cls, key: str, expires_s: int = 3600):
        return cls.client.presigned_get_object(
            bucket_name=cls.bucket,
            object_name=key,
            expires=timedelta(seconds=expires_s)
        )
