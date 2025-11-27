from datetime import datetime
from typing import List

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from wacruit.src.apps.history.models import History
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class HistoryRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_history(self) -> list[History]:
        query = select(History)
        return list(self.session.execute(query).scalars().all())

    def update_history(self, history_list: List[History]) -> List[History]:
        self.session.add_all(history_list)

        return history_list

    def get_start_date(self) -> datetime | None:
        query = select(History).where(History.history_key == "start_date")
        result = self.session.execute(query).scalar_one_or_none()

        if result is None:
            return None
        return datetime.strptime(result.history_value, "%Y-%m-%d")

    def delete_history(self, history_key: str) -> None:
        query = delete(History).where(History.history_key == history_key)
        self.session.execute(query)
