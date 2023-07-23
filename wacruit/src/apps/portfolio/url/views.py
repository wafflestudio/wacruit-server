from http import HTTPStatus
from typing import Annotated

import fastapi

from wacruit.src.apps.common.dependencies import CurrentUser
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.portfolio.url.schemas import PortfolioUrlResponse
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService

v1_router = fastapi.APIRouter(prefix="/url", tags=["url"])


@v1_router.get(path="/")
def list_portfolio_urls(
    current_user: CurrentUser,
    service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> ListResponse[PortfolioUrlResponse]:
    return ListResponse(items=service.list_portfolio_urls(current_user.id))


@v1_router.post(path="/")
def create_portfolio_url(
    current_user: CurrentUser,
    url: str,
    service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> PortfolioUrlResponse:
    return service.create_portfolio_url(current_user.id, url)


@v1_router.delete(
    path="/{portfolio_url_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_portfolio_url(
    current_user: CurrentUser,
    portfolio_url_id: int,
    service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> None:
    return service.delete_portfolio_url(current_user.id, portfolio_url_id)