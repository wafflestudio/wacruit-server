from wacruit.src.apps.portfolio.file.aws.config import s3_config
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.file.aws.s3.method import S3PresignedUrlMethod
from wacruit.src.apps.portfolio.file.aws.s3.utils import delete_object
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_post_url
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_url
from wacruit.src.apps.portfolio.file.aws.s3.utils import get_list_of_objects
from wacruit.src.apps.portfolio.file.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.file.exceptions import PortfolioNotFoundException
from wacruit.src.apps.portfolio.file.schemas import PortfolioNameResponse
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlResponse
from wacruit.src.utils.mixins import LoggingMixin

_1_MIN = 60
_10_MIN = 10 * _1_MIN
_1_MB = 1024 * 1024
_50_MB = 50 * _1_MB


class PortfolioFileService(LoggingMixin):
    def __init__(self):
        self._s3_config = s3_config
        self._s3_client = S3Client(region_name=self._s3_config.bucket_region)
        self._num_portfolio_limit = 1

    @staticmethod
    def get_portfolio_object_name(user_id: int, file_name: str) -> str:
        return f"{user_id}/{file_name}"

    def get_portfolio_list(self, user_id: int) -> list[str]:
        objects = get_list_of_objects(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_prefix=f"{user_id}/",
        )
        return ["".join(obj.split("/")[1:]) for obj in objects]

    def check_portfolio_limit(self, user_id: int) -> None:
        if len(self.get_portfolio_list(user_id)) > self._num_portfolio_limit - 1:
            raise NumPortfolioLimitException

    def check_portfolio_object_exist(self, user_id: int, file_name: str) -> None:
        if file_name not in self.get_portfolio_list(user_id):
            raise PortfolioNotFoundException

    def get_portfolios(
        self,
        user_id: int,
    ) -> list[PortfolioNameResponse]:
        return [
            PortfolioNameResponse(portfolio_name=obj)
            for obj in self.get_portfolio_list(user_id)
        ]

    def get_presigned_url_for_get_portfolio(
        self,
        user_id: int,
        file_name: str,
    ) -> PresignedUrlResponse:
        self.check_portfolio_object_exist(user_id, file_name)
        object_name = PortfolioFileService.get_portfolio_object_name(user_id, file_name)
        url = generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=S3PresignedUrlMethod.GET,
            method_parameters={
                "Bucket": self._s3_config.bucket_name,
                "Key": object_name,
            },
            expires_in=_10_MIN,
        )
        return PresignedUrlResponse(object_name=object_name, presigned_url=url)

    def get_presigned_url_for_post_portfolio(
        self,
        user_id: int,
        file_name: str,
    ) -> PresignedUrlResponse:
        self.check_portfolio_limit(user_id)
        object_name = PortfolioFileService.get_portfolio_object_name(user_id, file_name)
        # Note: Check AWS Docs for more info
        # https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html
        url, fields = generate_presigned_post_url(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_object=object_name,
            expires_in=_10_MIN,
            conditions=[
                # {"acl": "public-read"},
                # {"bucket": BUCKET_NAME},
                # ["starts-with", "$Content-Type", "image/"],
                ["content-length-range", 0, _50_MB],
            ],
        )
        return PresignedUrlResponse(
            object_name=object_name, presigned_url=url, fields=fields
        )

    def delete_portfolio(
        self,
        user_id: int,
        file_name: str,
    ) -> None:
        self.check_portfolio_object_exist(user_id, file_name)
        object_name = PortfolioFileService.get_portfolio_object_name(user_id, file_name)
        delete_object(self._s3_client.client, self._s3_config.bucket_name, object_name)

    def delete_all_portfolios(
        self,
        user_id: int,
    ) -> None:
        objects = get_list_of_objects(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_prefix=f"{user_id}/",
        )
        for obj in objects:
            delete_object(self._s3_client.client, self._s3_config.bucket_name, obj)

    def get_all_applicant_user_ids(self) -> list[int]:
        objects = get_list_of_objects(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_prefix="",
        )
        return list(
            set(
                int(obj.split("/")[0])
                for obj in objects
                if "/" in obj and obj.split("/")[0].isdigit()
            )
        )
