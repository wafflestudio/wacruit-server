from typing import Sequence

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from wacruit.src.apps.portfolio.file.exceptions import PortfolioNotFoundException
from wacruit.src.apps.portfolio.file.models import PortfolioFile
from wacruit.src.database.base import intpk
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class PortfolioFileRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_portfolio_files(
        self, user_id: int, recruiting_id: int
    ) -> Sequence[PortfolioFile]:
        query = (
            select(PortfolioFile)
            .where(PortfolioFile.user_id == user_id)
            .where(PortfolioFile.recruiting_id == recruiting_id)
        )
        return self.session.execute(query).scalars().all()

    def get_portfolio_file_by_id(self, portfolio_file_id: int) -> PortfolioFile:
        query = select(PortfolioFile).where(PortfolioFile.id == portfolio_file_id)
        try:
            return self.session.execute(query).scalar_one()
        except InvalidRequestError as exc:
            raise PortfolioNotFoundException() from exc

    def create_portfolio_file(self, portfolio_file: PortfolioFile) -> PortfolioFile:
        with self.transaction:
            self.session.add(portfolio_file)
        return portfolio_file

    def update_portfolio_file(self, portfolio_file: PortfolioFile) -> PortfolioFile:
        with self.transaction:
            self.session.merge(portfolio_file)
        return portfolio_file

    def delete_portfolio_file(self, id: int) -> None:
        with self.transaction:
            self.session.execute(delete(PortfolioFile).where(PortfolioFile.id == id))

    def delete_all_portfolio_files(self, user_id: int) -> None:
        with self.transaction:
            self.session.execute(
                delete(PortfolioFile).where(PortfolioFile.user_id == user_id)
            )
