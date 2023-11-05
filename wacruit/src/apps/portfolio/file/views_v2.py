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

v2_router = fastapi.APIRouter(prefix="/file", tags=["portfolio-file"])


@v2_router.get(
    path="/{term}",
    status_code=HTTPStatus.OK,
)
def get_list_of_portfolios(
    current_user: CurrentUser,
    term: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> ListResponse[PortfolioNameResponse]:
    portfolios = service.list_portfolios_from_db(current_user.id, term=term)
    return ListResponse(items=portfolios)


@v2_router.get(
    path="/url/download/{term}",
    responses=responses_from(PortfolioNotFoundException),
    status_code=HTTPStatus.OK,
)
def get_download_portfolio_url(
    current_user: CurrentUser,
    term: str,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PresignedUrlResponse:
    return service.get_presigned_url_for_get_portfolio(
        user_id=current_user.id,
        file_name=file_name,
        term=term,
    )


@v2_router.get(
    path="/url/upload/{term}",
    responses=responses_from(NumPortfolioLimitException),
    status_code=HTTPStatus.OK,
)
def get_upload_portfolio_url(
    current_user: CurrentUser,
    term: str,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PresignedUrlResponse:
    return service.get_presigned_url_for_post_portfolio(
        user_id=current_user.id,
        file_name=file_name,
        term=term,
    )


@v2_router.get(
    path="/url/check-upload-completed/{term}",
    responses=responses_from(NumPortfolioLimitException),
    status_code=HTTPStatus.OK,
)
def check_upload_portfolio_completed(
    current_user: CurrentUser,
    term: str,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PortfolioNameResponse:
    return service.register_portfolio_file_info_in_db(
        user_id=current_user.id,
        file_name=file_name,
        term=term,
    )


@v2_router.get(
    path="/url/check-upload-completed/{term}/update",
    responses=responses_from(NumPortfolioLimitException),
    status_code=HTTPStatus.OK,
)
def check_updated_upload_portfolio_completed(
    current_user: CurrentUser,
    term: str,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> PortfolioNameResponse:
    return service.update_portfolio_file_info_in_db(
        user_id=current_user.id,
        file_name=file_name,
        term=term,
    )


@v2_router.delete(
    path="/delete/{term}",
    responses=responses_from(PortfolioNotFoundException),
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_portfolio(
    current_user: CurrentUser,
    term: str,
    file_name: str,
    service: Annotated[PortfolioFileService, fastapi.Depends()],
) -> None:
    return service.delete_portfolio(
        user_id=current_user.id,
        file_name=file_name,
        term=term,
    )
