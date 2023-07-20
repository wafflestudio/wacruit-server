import time

from wacruit.src.apps.portfolio import schemas
from wacruit.src.apps.portfolio.aws import config
from wacruit.src.apps.portfolio.aws.s3 import client
from wacruit.src.apps.portfolio.aws.s3 import method
from wacruit.src.apps.portfolio.aws.s3 import utils as s3_utils
from wacruit.src.utils import mixins


class PortfolioService(mixins.LoggingMixin):
    def __init__(self):
        self._s3_client = client.S3Client()

    @staticmethod
    def get_portfolio_object_name(user_id: int, file_name: str) -> str:
        return f"{user_id}/{file_name}-{time.time()}"

    def get_presigned_url_for_upload_portfolio(self, object_name: str) -> schemas.PresignedUrlResponse:
        url = s3_utils.generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=method.S3PresignedUrlMethod.PUT,
            method_parameters={
                "Bucket": config.BUCKET_NAME,
                "Key": object_name,
            }
        )
        return schemas.PresignedUrlResponse(object_name=object_name, presigned_url=url)

    def get_presigned_url_for_get_portfolio(self, object_name: str) -> schemas.PresignedUrlResponse:
        url = s3_utils.generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=method.S3PresignedUrlMethod.GET,
            method_parameters={
                "Bucket": config.BUCKET_NAME,
                "Key": object_name,
            }
        )
        return schemas.PresignedUrlResponse(object_name=object_name, presigned_url=url)
