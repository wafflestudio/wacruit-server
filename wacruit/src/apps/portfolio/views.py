from typing import Annotated

import fastapi

from wacruit.src.apps.common.dependencies import CurrentUser
from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.portfolio.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.exceptions import PortfolioNotFoundException
from wacruit.src.apps.portfolio.schemas import PortfolioNameResponse
from wacruit.src.apps.portfolio.schemas import PresignedUrlResponse
from wacruit.src.apps.portfolio.services import PortfolioService

v1_router = fastapi.APIRouter(prefix="/v1/portfolios", tags=["portfolios"])


@v1_router.get("/")
def get_list_of_portfolios(
    current_user: CurrentUser,
    portfolio_service: Annotated[PortfolioService, fastapi.Depends()],
) -> list[PortfolioNameResponse]:
    return portfolio_service.get_portfolio_responses(current_user.id)


@v1_router.get("/url/download/{file_name}", responses=responses_from(PortfolioNotFoundException))
def get_download_portfolio_url(
    current_user: CurrentUser,
    file_name: str,
    portfolio_service: Annotated[PortfolioService, fastapi.Depends()],
) -> PresignedUrlResponse:
    if file_name not in portfolio_service.get_portfolio_list(current_user.id):
        raise PortfolioNotFoundException
    object_name = portfolio_service.get_portfolio_object_name(
        user_id=current_user.id,
        file_name=file_name,
    )
    return portfolio_service.get_presigned_url_for_get_portfolio(object_name)


@v1_router.get("/url/upload/{file_name}", responses=responses_from(NumPortfolioLimitException))
def get_upload_portfolio_url(
    current_user: CurrentUser,
    file_name: str,
    portfolio_service: Annotated[PortfolioService, fastapi.Depends()],
) -> PresignedUrlResponse:
    if len(portfolio_service.get_portfolio_list(current_user.id)) > 0:
        raise NumPortfolioLimitException
    object_name = portfolio_service.get_portfolio_object_name(
        user_id=current_user.id,
        file_name=file_name,
    )
    return portfolio_service.get_presigned_url_for_upload_portfolio(object_name)


@v1_router.get("/url/delete/{file_name}", responses=responses_from(PortfolioNotFoundException))
def get_delete_portfolio_url(
    current_user: CurrentUser,
    file_name: str,
    portfolio_service: Annotated[PortfolioService, fastapi.Depends()],
) -> None:
    if file_name not in portfolio_service.get_portfolio_list(current_user.id):
        raise PortfolioNotFoundException
    object_name = portfolio_service.get_portfolio_object_name(
        user_id=current_user.id,
        file_name=file_name,
    )
    return portfolio_service.delete_portfolio(object_name)
