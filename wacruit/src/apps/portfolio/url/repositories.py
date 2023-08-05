from typing import Sequence

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotFound
from wacruit.src.apps.portfolio.url.models import PortfolioUrl
from wacruit.src.database.base import intpk
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class PortfolioUrlRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_portfolio_urls(self, user_id: int) -> Sequence[PortfolioUrl]:
        query = select(PortfolioUrl).where(PortfolioUrl.user_id == user_id)
        return self.session.execute(query).scalars().all()

    def get_portfolio_url_by_id(self, portfolio_url_id: int) -> PortfolioUrl:
        query = select(PortfolioUrl).where(PortfolioUrl.id == portfolio_url_id)
        try:
            return self.session.execute(query).scalar_one()
        except InvalidRequestError as exc:
            raise PortfolioUrlNotFound() from exc

    def create_portfolio_url(self, portfolio_url: PortfolioUrl) -> PortfolioUrl:
        with self.transaction:
            self.session.add(portfolio_url)
        return portfolio_url

    def update_portfolio_url(self, portfolio_url: PortfolioUrl) -> PortfolioUrl:
        with self.transaction:
            self.session.merge(portfolio_url)
        return portfolio_url

    def delete_portfolio_url(self, id: int) -> None:
        with self.transaction:
            self.session.execute(delete(PortfolioUrl).where(PortfolioUrl.id == id))

    def delete_all_portfolio_urls(self, user_id: int) -> None:
        with self.transaction:
            self.session.execute(
                delete(PortfolioUrl).where(PortfolioUrl.user_id == user_id)
            )

    def get_all_applicant_user_ids(self) -> Sequence[intpk]:
        query = select(PortfolioUrl.user_id).where(
            PortfolioUrl.user_id.isnot(None)
        ).distinct()
        return self.session.execute(query).scalars().all()
