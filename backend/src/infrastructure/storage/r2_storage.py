import boto3
from botocore.client import Config

from core.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET,
    R2_ENDPOINT,
    R2_REGION,
    R2_SECRET_ACCESS_KEY,
)
from domain.interfaces.storage_interface import StorageInterface


class R2Storage(StorageInterface):
    def __init__(self):
        self.bucket = R2_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name=R2_REGION,
            config=Config(signature_version="s3v4"),
        )

    def save(self, file_bytes: bytes, filename: str) -> str:
        self.client.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=file_bytes,
        )
        return filename

    def get_file(self, file_key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=file_key)
        return response["Body"].read()
