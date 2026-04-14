from typing import cast

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from wacruit.src.apps.portfolio.file.aws.config import storage_config
from wacruit.src.utils.singleton import SingletonMeta


class S3Client(metaclass=SingletonMeta):
    _client: BaseClient

    def __init__(self):
        self._client = cast(
            BaseClient,
            boto3.client(
                "s3",
                region_name=storage_config.region,
                endpoint_url=storage_config.endpoint_url,
                aws_access_key_id=storage_config.access_key_id,
                aws_secret_access_key=storage_config.secret_access_key,
                config=Config(s3={"addressing_style": storage_config.addressing_style}),
            ),
        )

    @property
    def client(self):
        return self._client
