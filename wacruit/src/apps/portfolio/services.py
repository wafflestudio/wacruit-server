from wacruit.src.apps.portfolio.schemas import PortfolioNameResponse
from wacruit.src.apps.portfolio.schemas import PresignedUrlResponse
from wacruit.src.apps.portfolio.aws.config import BUCKET_NAME
from wacruit.src.apps.portfolio.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.aws.s3.method import S3PresignedUrlMethod
from wacruit.src.apps.portfolio.aws.s3.utils import get_list_of_objects
from wacruit.src.apps.portfolio.aws.s3.utils import generate_presigned_url
from wacruit.src.utils.mixins import LoggingMixin


class PortfolioService(LoggingMixin):
    def __init__(self):
        self._s3_client = S3Client()

    @staticmethod
    def get_portfolio_object_name(user_id: int, file_name: str) -> str:
        return f"{user_id}/{file_name}"

    def get_portfolio_list(self, user_id: int) -> list[str]:
        objects = get_list_of_objects(
            s3_client=self._s3_client.client,
            s3_bucket=BUCKET_NAME,
            s3_prefix=f"{user_id}/",
        )
        return [obj[len(str(user_id)) + 1:] for obj in objects]

    def get_portfolio_responses(
        self,
        user_id: int,
    ) -> list[schemas.PortfolioNameResponse]:
        return [
            schemas.PortfolioNameResponse(portfolio_name=obj[len(str(user_id)) + 1:])
            for obj in self.get_portfolio_list(user_id)
        ]

    def get_presigned_url_for_upload_portfolio(
        self,
        object_name: str,
    ) -> PresignedUrlResponse:
        url = generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=S3PresignedUrlMethod.PUT,
            method_parameters={
                "Bucket": BUCKET_NAME,
                "Key": object_name,
            }
        )
        return PresignedUrlResponse(object_name=object_name, presigned_url=url)

    def get_presigned_url_for_get_portfolio(
        self,
        object_name: str,
    ) -> PresignedUrlResponse:
        url = generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=S3PresignedUrlMethod.GET,
            method_parameters={
                "Bucket": BUCKET_NAME,
                "Key": object_name,
            }
        )
        return PresignedUrlResponse(object_name=object_name, presigned_url=url)

    def get_presigned_url_for_delete_portfolio(
        self,
        object_name: str,
    ) -> PresignedUrlResponse:
        url = generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=S3PresignedUrlMethod.DELETE,
            method_parameters={
                "Bucket": BUCKET_NAME,
                "Key": object_name,
            }
        )
        return PresignedUrlResponse(object_name=object_name, presigned_url=url)
