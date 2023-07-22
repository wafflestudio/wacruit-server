import boto3

from wacruit.src.apps.portfolio.aws.config import REGION
from wacruit.src.utils.singleton import SingletonMeta


class S3Client(metaclass=SingletonMeta):
    def __init__(self, region_name: str = REGION):
        self._client = boto3.client("s3", region_name=region_name)

    @property
    def client(self):
        return self._client
