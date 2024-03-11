from typing import cast

import boto3
from botocore.client import BaseClient

from wacruit.src.utils.singleton import SingletonMeta


class S3Client(metaclass=SingletonMeta):
    _client: BaseClient

    def __init__(self, region_name: str = "ap-northeast-2"):
        self._client = cast(BaseClient, boto3.client("s3", region_name=region_name))

    @property
    def client(self):
        return self._client
