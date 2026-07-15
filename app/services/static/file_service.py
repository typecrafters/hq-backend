from datetime import timedelta
from os import fstat, path
from minio import Minio, S3Error
from app.config.settings import settings

class FileService:
    protected = ['system/']
    essentials = { 'system/placeholder.svg': 'placeholder.svg' }
    bucket = settings.s3_bucket
    client = Minio(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=settings.s3_secure,
    )

    @classmethod
    def asset(cls, filename: str) -> str:
        return path.resolve(path.join(path.dirname(__file__), '..', '..', 'assets', filename))

    @classmethod
    def ensure_essential_files(cls):
        for key, filepath in cls.essentials.items():
            try:
                cls.client.stat_object(bucket_name=cls.bucket, object_name=key)
            except S3Error as e:
                if e.code == 'NoSuchKey':
                    abspath = cls.asset(filepath)
                    with open(abspath, 'rb') as file:
                        size = path.getsize(abspath)
                        cls.client.put_object(cls.bucket, key, file, size)

    @classmethod
    def sign_upload(cls, key: str, expires_s: int = 60):
        return cls.client.presigned_put_object(
            bucket_name=cls.bucket,
            object_name=key,
            expires=timedelta(seconds=expires_s)
        )

    @classmethod
    def sign_download(cls, key: str | None, expires_s: int = 3600):
        if not key:
            return key
        return cls.client.presigned_get_object(
            bucket_name=cls.bucket,
            object_name=key,
            expires=timedelta(seconds=expires_s)
        )
    
    @classmethod
    def delete(cls, key: str) -> bool:
        if any([key.lstrip('/').lower().startswith(p) for p in cls.protected]):
            return False
        try:
            cls.client.remove_object(cls.bucket, key)
            return True
        except:
            return False