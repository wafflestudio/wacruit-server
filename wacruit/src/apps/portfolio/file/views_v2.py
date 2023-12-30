from http import HTTPStatus
from typing import Annotated

import fastapi

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.portfolio.file.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.file.exceptions import PortfolioNotFoundException
from wacruit.src.apps.portfolio.file.schemas import PortfolioFileRequest
from wacruit.src.apps.portfolio.file.schemas import PortfolioFileResponse
from wacruit.src.apps.portfolio.file.schemas import PortfolioRequest
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlResponse
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlWithIdResponse
from wacruit.src.apps.portfolio.file.services_v2 import PortfolioFileService
from wacruit.src.apps.user.dependencies import CurrentUser

v2_router = fastapi.APIRouter(prefix="/file", tags=["portfolio-file"])


@v2_router.get(
    path="",
    status_code=HTTPStatus.OK,
)
def get_list_of_portfolios(
    current_user: CurrentUser,
    recruiting_id: int,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> ListResponse[PortfolioFileResponse]:
    portfolios = service.list_portfolios_from_db(
        current_user.id, recruiting_id=recruiting_id
    )
    return ListResponse(items=portfolios)


@v2_router.get(
    path="/url/download/{portfolio_file_id}",
    responses=responses_from(PortfolioNotFoundException),
    status_code=HTTPStatus.OK,
)
def get_download_portfolio_url(
    current_user: CurrentUser,
    portfolio_file_id: int,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PresignedUrlResponse:
    return service.get_presigned_url_for_get_portfolio(
        user_id=current_user.id, portfolio_file_id=portfolio_file_id
    )


@v2_router.get(
    path="/url/upload/",
    responses=responses_from(NumPortfolioLimitException),
    status_code=HTTPStatus.OK,
)
def get_upload_portfolio_url(
    current_user: CurrentUser,
    request: PortfolioFileRequest,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PresignedUrlWithIdResponse:
    return service.get_presigned_url_for_post_portfolio(
        user_id=current_user.id,
        file_name=request.file_name,
        recruiting_id=request.recruiting_id,
    )


@v2_router.get(
    path="/url/check-upload-completed/{portfolio_file_id}",
    responses=responses_from(NumPortfolioLimitException),
    status_code=HTTPStatus.OK,
)
def check_upload_portfolio_completed(
    current_user: CurrentUser,
    portfolio_file_id: int,
    request: PortfolioFileRequest,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PortfolioFileResponse:
    return service.register_portfolio_file_info_in_db(
        user_id=current_user.id,
        portfolio_file_id=portfolio_file_id,
        file_name=request.file_name,
        recruiting_id=request.recruiting_id,
    )


@v2_router.get(
    path="/url/check-upload-completed/update/{portfolio_file_id}",
    responses=responses_from(NumPortfolioLimitException),
    status_code=HTTPStatus.OK,
)
def check_updated_upload_portfolio_completed(
    current_user: CurrentUser,
    portfolio_file_id: int,
    request: PortfolioFileRequest,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PortfolioFileResponse:
    return service.update_portfolio_file_info_in_db(
        user_id=current_user.id,
        portfolio_file_id=portfolio_file_id,
        new_file_name=request.file_name,
    )


@v2_router.delete(
    path="/delete/{portfolio_file_id}",
    responses=responses_from(PortfolioNotFoundException),
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_portfolio(
    current_user: CurrentUser,
    portfolio_file_id: int,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> None:
    return service.delete_portfolio(
        user_id=current_user.id,
        portfolio_file_id=portfolio_file_id,
    )
