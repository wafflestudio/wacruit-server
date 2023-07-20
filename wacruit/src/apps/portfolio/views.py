from typing import Annotated

import fastapi

from wacruit.src.apps.common import dependencies as common_deps
from wacruit.src.apps.portfolio import services
from wacruit.src.apps.portfolio import schemas

v1_router = fastapi.APIRouter(prefix="/v1/portfolios", tags=["portfolios"])


@v1_router.get("/url/get")
def get_portfolio(
    request: fastapi.Request,
    current_user: common_deps.CurrentUser,
    upload_portfolio_request: schemas.UploadPortfolioUrlRequest,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    object_name = portfolio_service.get_portfolio_object_name(
        current_user.id, upload_portfolio_request.file_name
    )
    return portfolio_service.get_presigned_url_for_get_portfolio(object_name)


@v1_router.get("/url/upload")
def get_upload_portfolio_url(
    request: fastapi.Request,
    current_user: common_deps.CurrentUser,
    upload_portfolio_request: schemas.UploadPortfolioUrlRequest,
    portfolio_service: Annotated[services.PortfolioService, fastapi.Depends()],
):
    object_name = portfolio_service.get_portfolio_object_name(
        current_user.id, upload_portfolio_request.file_name
    )
    return portfolio_service.get_presigned_url_for_get_portfolio(object_name)
