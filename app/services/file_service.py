from datetime import timedelta
from minio import Minio

class FileService:
    client: Minio

    def __init__(self, client: Minio):
        self.client = client

    def sign_upload(self, bucket: str, key: str, expires_s: int = 60):
        return self.client.presigned_put_object(
            bucket_name=bucket,
            object_name=key,
            expires=timedelta(seconds=expires_s)
        )
    
    def sign_download(self, bucket: str, key: str, expires_s: int = 3600):
        return self.client.presigned_get_object(
            bucket_name=bucket,
            object_name=key,
            expires=timedelta(seconds=expires_s)
        )