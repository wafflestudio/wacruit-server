from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.portfolio.url.exceptions import InValidGenerationException
from wacruit.src.apps.portfolio.url.exceptions import NumPortfolioUrlLimitException
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotAuthorized
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotFound
from wacruit.src.apps.portfolio.url.models import PortfolioUrl
from wacruit.src.apps.portfolio.url.repositories import PortfolioUrlRepository
from wacruit.src.apps.portfolio.url.schemas import PortfolioUrlResponse
from wacruit.src.apps.recruiting.repositories import RecruitingRepository


class PortfolioUrlService:
    def __init__(
        self,
        portfolio_url_repository: Annotated[PortfolioUrlRepository, Depends()],
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
    ) -> None:
        self._portfolio_url_repository = portfolio_url_repository
        self._recruiting_repository = recruiting_repository
        self._num_url_limit = 3

    def _validate_generation(self, generation: int) -> None:
        recruiting = self._recruiting_repository.get_recruiting_by_id(generation)
        if (recruiting is None) or (not recruiting.is_active):
            raise InValidGenerationException

    def create_portfolio_url(
        self,
        user_id: int,
        url: str,
        generation: int,
    ) -> PortfolioUrlResponse:
        self._validate_generation(generation)
        num_portfolios = len(
            self._portfolio_url_repository.get_portfolio_urls_in_generation(
                user_id, generation
            )
        )
        if num_portfolios >= self._num_url_limit:
            raise NumPortfolioUrlLimitException
        portfolio_url = self._portfolio_url_repository.create_portfolio_url(
            PortfolioUrl(user_id=user_id, url=url, generation=generation)
        )
        return PortfolioUrlResponse.from_orm(portfolio_url)

    def list_portfolio_urls(
        self, user_id: int, generation: int
    ) -> list[PortfolioUrlResponse]:
        self._validate_generation(generation)
        portfolio_urls = (
            self._portfolio_url_repository.get_portfolio_urls_in_generation(
                user_id, generation
            )
        )
        return [
            PortfolioUrlResponse.from_orm(portfolio_url)
            for portfolio_url in portfolio_urls
        ]

    def delete_portfolio_url(self, user_id: int, portfolio_url_id: int) -> None:
        portfolio_url = self._portfolio_url_repository.get_portfolio_url_by_id(
            portfolio_url_id
        )
        if not portfolio_url:
            raise PortfolioUrlNotFound

        if portfolio_url.user_id != user_id:
            raise PortfolioUrlNotAuthorized

        self._portfolio_url_repository.delete_portfolio_url(portfolio_url_id)

    def delete_all_portfolio_urls(self, user_id: int, generation: int) -> None:
        self._validate_generation(generation)
        self._portfolio_url_repository.delete_all_portfolio_urls_in_generation(
            user_id, generation
        )

    def get_all_applicant_user_ids(self) -> list[int]:
        return list(self._portfolio_url_repository.get_all_applicant_user_ids())

    def update_portfolio_url(
        self, user_id: int, portfolio_url_id: int, url: str
    ) -> PortfolioUrlResponse:
        portfolio_url = self._portfolio_url_repository.get_portfolio_url_by_id(
            portfolio_url_id
        )

        if not portfolio_url:
            raise PortfolioUrlNotFound

        if portfolio_url.user_id != user_id:
            raise PortfolioUrlNotAuthorized

        portfolio_url.url = url
        self._portfolio_url_repository.update_portfolio_url(portfolio_url)
        return PortfolioUrlResponse.from_orm(portfolio_url)
