from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.portfolio.file.aws.config import s3_config
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.file.aws.s3.method import S3PresignedUrlMethod
from wacruit.src.apps.portfolio.file.aws.s3.utils import delete_object
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_post_url
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_url
from wacruit.src.apps.portfolio.file.aws.s3.utils import get_list_of_objects
from wacruit.src.apps.portfolio.file.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.file.exceptions import PortfolioNotFoundException
from wacruit.src.apps.portfolio.file.models import PortfolioFile
from wacruit.src.apps.portfolio.file.repositories import PortfolioFileRepository
from wacruit.src.apps.portfolio.file.schemas import PortfolioFileResponse
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlResponse
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlWithIdResponse
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.utils.mixins import LoggingMixin

_1_MIN = 60
_10_MIN = 10 * _1_MIN
_1_MB = 1024 * 1024
_50_MB = 50 * _1_MB


class PortfolioFileService(LoggingMixin):
    def __init__(
        self,
        portfolio_file_repository: Annotated[PortfolioFileRepository, Depends()],
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
    ):
        self._portfolio_file_repository = portfolio_file_repository
        self._recruiting_repository = recruiting_repository
        self._s3_config = s3_config
        self._s3_client = S3Client(region_name=self._s3_config.bucket_region)
        self._num_portfolio_limit = 1

    @staticmethod
    def _get_portfolio_object_name(
        user_id: int, file_name: str, recruiting_id: int
    ) -> str:
        return f"{recruiting_id}/{user_id}/{file_name}"

    def _get_portfolio_list(self, user_id: int, recruiting_id: int) -> list[str]:
        portfolios = self._portfolio_file_repository.get_portfolio_files(
            user_id=user_id,
            recruiting_id=recruiting_id,
        )
        return [portfolio.file_name for portfolio in portfolios]

    def _check_portfolio_limit(self, user_id: int, recruiting_id: int) -> None:
        if (
            len(self._get_portfolio_list(user_id, recruiting_id))
            > self._num_portfolio_limit - 1
        ):
            raise NumPortfolioLimitException

    def _check_portfolio_object_exist(
        self,
        user_id: int,
        file_name: str,
        recruiting_id: int,
    ) -> None:
        if file_name not in self._get_portfolio_list(user_id, recruiting_id):
            raise PortfolioNotFoundException

    def get_presigned_url_for_get_portfolio(
        self, user_id: int, portfolio_file_id: int
    ) -> PresignedUrlResponse:
        portfolio_file_info = self._portfolio_file_repository.get_portfolio_file_by_id(
            portfolio_file_id
        )
        self._check_portfolio_object_exist(
            user_id, portfolio_file_info.file_name, portfolio_file_info.recruiting_id
        )
        object_name = self._get_portfolio_object_name(
            user_id, portfolio_file_info.file_name, portfolio_file_info.recruiting_id
        )
        url = generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=S3PresignedUrlMethod.GET,
            method_parameters={
                "Bucket": self._s3_config.bucket_name,
                "Key": object_name,
            },
            expires_in=_10_MIN,
        )
        return PresignedUrlResponse(
            object_name=object_name, presigned_url=url, fields={}
        )

    def get_presigned_url_for_post_portfolio(
        self,
        user_id: int,
        file_name: str,
        recruiting_id: int,
    ) -> PresignedUrlWithIdResponse:
        self._recruiting_repository.validate_recruiting_id(recruiting_id)
        self._check_portfolio_limit(user_id, recruiting_id)
        object_name = self._get_portfolio_object_name(user_id, file_name, recruiting_id)
        # Note: Check AWS Docs for more info
        # https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html
        url, fields = generate_presigned_post_url(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_object=object_name,
            expires_in=_10_MIN,
            conditions=[
                ["content-length-range", 0, _50_MB],
            ],
        )
        portfolio_file = self._portfolio_file_repository.create_portfolio_file(
            PortfolioFile(
                user_id=user_id,
                file_name=file_name,
                recruiting_id=recruiting_id,
            )
        )
        return PresignedUrlWithIdResponse(
            object_name=object_name,
            presigned_url=url,
            fields=fields,
            portfolio_file_id=portfolio_file.id,
        )

    def list_portfolios_from_db(
        self,
        user_id: int,
        recruiting_id: int,
    ) -> list[PortfolioFileResponse]:
        portfolio_files = self._portfolio_file_repository.get_portfolio_files(
            user_id=user_id,
            recruiting_id=recruiting_id,
        )
        return [
            PortfolioFileResponse.from_orm(portfolio_file)
            for portfolio_file in portfolio_files
        ]

    def register_portfolio_file_info_in_db(
        self,
        user_id: int,
        portfolio_file_id: int,
    ) -> PortfolioFileResponse:
        self._portfolio_file_repository.update_portfolio_file(
            portfolio_file_id=portfolio_file_id,
            user_id=user_id,
        )
        portfolio_file = self._portfolio_file_repository.get_portfolio_file_by_id(
            portfolio_file_id
        )
        return PortfolioFileResponse.from_orm(portfolio_file)

    def delete_portfolio(
        self,
        user_id: int,
        portfolio_file_id: int,
    ) -> None:
        portfolio_file = self._portfolio_file_repository.get_portfolio_file_by_id(
            portfolio_file_id
        )
        self._recruiting_repository.validate_recruiting_id(portfolio_file.recruiting_id)
        self._check_portfolio_object_exist(
            user_id, portfolio_file.file_name, portfolio_file.recruiting_id
        )
        object_name = self._get_portfolio_object_name(
            user_id, portfolio_file.file_name, portfolio_file.recruiting_id
        )
        delete_object(self._s3_client.client, self._s3_config.bucket_name, object_name)
        self._portfolio_file_repository.delete_portfolio_file(portfolio_file_id)

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
        self.delete_all_portfolios(user_id)

    def get_all_applicant_user_ids(self) -> list[int]:
        objects = get_list_of_objects(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_prefix="",
        )
        return list(set(int(obj.split("/")[0]) for obj in objects))
