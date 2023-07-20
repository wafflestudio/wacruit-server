import boto3

from wacruit.src.apps.portfolio.aws import config
from wacruit.src.utils import singleton as singleton_utils


class S3Client(metaclass=singleton_utils.SingletonMeta):
    def __init__(self, region_name: str = config.REGION):
        self._client = boto3.client("s3", region_name=region_name)

    @property
    def client(self):
        return self._client
