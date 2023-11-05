from http import HTTPStatus
from typing import Annotated

import fastapi
from fastapi import Response

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.portfolio.url.exceptions import NumPortfolioUrlLimitException
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotAuthorized
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotFound
from wacruit.src.apps.portfolio.url.schemas import PortfolioUrlRequest
from wacruit.src.apps.portfolio.url.schemas import PortfolioUrlResponse
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.user.dependencies import CurrentUser

v2_router = fastapi.APIRouter(prefix="/url", tags=["portfolio-url"])


@v2_router.get(
    path="/{term}",
    status_code=HTTPStatus.OK,
)
def list_portfolio_urls(
    current_user: CurrentUser,
    term: str,
    service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> ListResponse[PortfolioUrlResponse]:
    return ListResponse(items=service.list_portfolio_urls(current_user.id, term))


@v2_router.post(
    path="/{term}",
    responses=responses_from(NumPortfolioUrlLimitException),
    status_code=HTTPStatus.CREATED,
)
def register_portfolio_url(
    response: Response,
    current_user: CurrentUser,
    term: str,
    request: PortfolioUrlRequest,
    service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> PortfolioUrlResponse:
    response.headers["Access-Control-Allow-Origin"] = "*"
    return service.create_portfolio_url(current_user.id, request.url, term)


@v2_router.delete(
    path="/{portfolio_url_id}",
    responses=responses_from(PortfolioUrlNotAuthorized, PortfolioUrlNotFound),
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_portfolio_url(
    current_user: CurrentUser,
    portfolio_url_id: int,
    service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> None:
    return service.delete_portfolio_url(current_user.id, portfolio_url_id)


@v2_router.put(
    path="/{portfolio_url_id}",
    responses=responses_from(PortfolioUrlNotAuthorized, PortfolioUrlNotFound),
    status_code=HTTPStatus.OK,
)
def update_portfolio_url(
    current_user: CurrentUser,
    portfolio_url_id: int,
    request: PortfolioUrlRequest,
    service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> PortfolioUrlResponse:
    return service.update_portfolio_url(current_user.id, portfolio_url_id, request.url)
