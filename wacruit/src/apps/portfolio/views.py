from typing import Annotated

import fastapi

from wacruit.src.apps.common import dependencies as common_deps
from wacruit.src.apps.portfolio import services
from wacruit.src.apps.portfolio import schemas

v1_router = fastapi.APIRouter(prefix="/v1/portfolios", tags=["portfolios"])

@v1_router.get("/url")
def get_dum():
    return {"dummy": "dummy"}

@v1_router.get("/url/download/{file_name}")
def get_download_portfolio_url(
    current_user: common_deps.CurrentUser,
    file_name: str,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    object_name = portfolio_service.get_portfolio_object_name(current_user.id, file_name)
    return portfolio_service.get_presigned_url_for_get_portfolio(object_name)


@v1_router.get("/url/upload/{file_name}")
def get_upload_portfolio_url(
    current_user: common_deps.CurrentUser,
    file_name: str,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    object_name = portfolio_service.get_portfolio_object_name(current_user.id, file_name)
    return portfolio_service.get_presigned_url_for_get_portfolio(object_name)
