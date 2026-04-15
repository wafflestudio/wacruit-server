from typing import cast

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from wacruit.src.apps.portfolio.file.aws.config import StorageConfig, storage_config


class S3Client:
    _client: BaseClient

    def __init__(self, config: StorageConfig | None = None):
        config = config or storage_config
        self._client = cast(
            BaseClient,
            boto3.client(
                "s3",
                region_name=config.region,
                endpoint_url=config.endpoint_url,
                aws_access_key_id=config.access_key_id,
                aws_secret_access_key=config.secret_access_key,
                config=Config(s3={"addressing_style": config.addressing_style}),
            ),
        )

    @property
    def client(self):
        return self._client
