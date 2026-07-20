from os import path
from typing import Literal

from botocore.config import Config
from app.config.settings import settings


class FileService:
    protected = ['system/']
    essentials = {'system/placeholder.svg': 'placeholder.svg'}
    bucket = settings.s3_bucket
    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            from boto3 import client as boto3_client
            if not settings.s3_endpoint:
                raise RuntimeError(
                    'S3 endpoint is not configured. Set S3_ENDPOINT env var.'
                )
            cls._client = boto3_client(
                's3',
                endpoint_url=settings.s3_endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                config=Config(signature_version='s3v4')
            )
        return cls._client

    @classmethod
    def __asset(cls, filename: str) -> str:
        return path.resolve(path.join(path.dirname(__file__), '..', '..', 'assets', filename))

    @classmethod
    def ensure_essential_files(cls):
        c = cls._get_client()
        for key, filepath in cls.essentials.items():
            try:
                c.head_object(Bucket=cls.bucket, Key=key)
            except c.exceptions.ClientError as e:
                if not e.response['Error']['Code'] == '404':
                    raise e
                abspath = cls.__asset(filepath)
                with open(abspath, 'rb') as file:
                    c.put_object(
                        Bucket=cls.bucket, Key=filepath, Body=file.read())

    @classmethod
    def __sign(cls, method: Literal['put_object', 'get_object'], key: str, exp: int, content_type: str | None = None) -> str | None:
        if not key:
            return None
        c = cls._get_client()
        params = {'Bucket': cls.bucket, 'Key': key}
        if content_type is not None:
            params['ContentType'] = content_type
        return c.generate_presigned_url(
            method,
            Params=params,
            ExpiresIn=exp
        )

    @classmethod
    def sign_put(cls, key: str, content_type: str, exp: int = 60) -> str | None:
        if not key:
            return None
        return cls.__sign('put_object', key, exp, content_type)

    @classmethod
    def sign_get(cls, key: str, exp: int = 60) -> str | None:
        if not key:
            return None
        return cls.__sign('get_object', key, exp)

    @classmethod
    def delete(cls, key: str) -> bool:
        if not key:
            return False
        if any([key.lstrip('/').lower().startswith(p) for p in cls.protected]):
            return False
        try:
            c = cls._get_client()
            c.delete_objects(
                Bucket=cls.bucket,
                Delete={
                    'Objects': [{ 'Key': key }]
                }
            )
            return True
        except:
            return False
