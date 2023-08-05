from http import HTTPStatus
from typing import Annotated

import fastapi

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.portfolio.file.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.file.exceptions import PortfolioNotFoundException
from wacruit.src.apps.portfolio.file.schemas import PortfolioNameResponse
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlResponse
from wacruit.src.apps.portfolio.file.services import PortfolioFileService
from wacruit.src.apps.user.dependencies import CurrentUser

v1_router = fastapi.APIRouter(prefix="/file", tags=["portfolio-file"])


@v1_router.get(
    path="",
    status_code=HTTPStatus.OK,
)
def get_list_of_portfolios(
    current_user: CurrentUser,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> ListResponse[PortfolioNameResponse]:
    portfolios = service.get_portfolios(current_user.id)
    return ListResponse(items=portfolios)


@v1_router.get(
    path="/url/download/",
    responses=responses_from(PortfolioNotFoundException),
    status_code=HTTPStatus.OK,
)
def get_download_portfolio_url(
    current_user: CurrentUser,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PresignedUrlResponse:
    return service.get_presigned_url_for_get_portfolio(
        user_id=current_user.id,
        file_name=file_name,
    )


@v1_router.get(
    path="/url/upload/",
    responses=responses_from(NumPortfolioLimitException),
    status_code=HTTPStatus.OK,
)
def get_upload_portfolio_url(
    current_user: CurrentUser,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PresignedUrlResponse:
    return service.get_presigned_url_for_post_portfolio(
        user_id=current_user.id,
        file_name=file_name,
    )


@v1_router.delete(
    path="/delete/",
    responses=responses_from(PortfolioNotFoundException),
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_portfolio(
    current_user: CurrentUser,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> None:
    return service.delete_portfolio(
        user_id=current_user.id,
        file_name=file_name,
    )
