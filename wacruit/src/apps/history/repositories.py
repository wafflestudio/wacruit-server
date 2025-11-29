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
        keys = [h.history_key for h in history_list]
        existing_key = (
            self.session.query(History).filter(History.history_key.in_(keys)).all()
        )
        existing_map = {r.history_key: r for r in existing_key}

        for item in history_list:
            if item.history_key in existing_map:
                # if existed, update
                existing = existing_map[item.history_key]
                existing.history_value = item.history_value
                existing.history_unit = item.history_unit
            else:
                # if not existed, insert
                self.session.add(item)

        return history_list

    def get_start_date(self) -> datetime | None:
        query = select(History).where(History.history_key == "start_date")
        result = self.session.execute(query).scalar_one_or_none()

        if result is None:
            return None
        return datetime.strptime(result.history_value, "%Y-%m-%d")

    def delete_history(self, history_key: str) -> bool:
        history = self.session.query(History).filter_by(history_key=history_key).first()
        if not history:
            return False
        self.session.delete(history)
        return True
