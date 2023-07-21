from typing import Annotated

import fastapi

from wacruit.src.apps.common import dependencies as common_deps
from wacruit.src.apps.portfolio import exceptions
from wacruit.src.apps.portfolio import services
from wacruit.src.apps.portfolio import schemas

v1_router = fastapi.APIRouter(prefix="/v1/portfolios", tags=["portfolios"])


@v1_router.get("/", response_model=list[schemas.PortfolioNameResponse])
def get_list_of_portfolios(
    current_user: common_deps.CurrentUser,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    return portfolio_service.get_portfolio_responses(current_user.id)


@v1_router.get("/url/download/{file_name}")
def get_download_portfolio_url(
    current_user: common_deps.CurrentUser,
    file_name: str,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    object_name = portfolio_service.get_portfolio_object_name(
        user_id=current_user.id,
        file_name=file_name,
    )
    return portfolio_service.get_presigned_url_for_get_portfolio(object_name)


@v1_router.get("/url/upload/{file_name}")
def get_upload_portfolio_url(
    current_user: common_deps.CurrentUser,
    file_name: str,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    if len(portfolio_service.get_portfolio_list(current_user.id)) > 0:
        raise exceptions.NumPortfolioLimitException
    object_name = portfolio_service.get_portfolio_object_name(
        user_id=current_user.id,
        file_name=file_name,
    )
    return portfolio_service.get_presigned_url_for_upload_portfolio(object_name)


@v1_router.get("/url/delete/{file_name}")
def get_delete_portfolio_url(
    current_user: common_deps.CurrentUser,
    file_name: str,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    if file_name not in portfolio_service.get_portfolio_list(current_user.id):
        raise exceptions.PortfolioNotFoundException
    object_name = portfolio_service.get_portfolio_object_name(
        user_id=current_user.id,
        file_name=file_name,
    )
    return portfolio_service.get_presigned_url_for_delete_portfolio(object_name)
