from datetime import datetime

from fastapi import Depends
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

    def update_history(self, history: History) -> History:
        history_key = history.history_key
        history_value = history.history_value

        with self.transaction:
            query = select(History).where(History.history_key == history_key)
            result = self.session.execute(query).scalar_one_or_none()
            if result:
                result.history_value = history_value
            else:
                result = History(history_key=history_key, history_value=history_value)
                self.session.add(result)

        return history

    def get_start_date(self) -> datetime | None:
        query = select(History).where(History.history_key == "start_date")
        result = self.session.execute(query).scalar_one_or_none()

        if result is None:
            return None
        return datetime.strptime(result.history_value, "%Y-%m-%d")
