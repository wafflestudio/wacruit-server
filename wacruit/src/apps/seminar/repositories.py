from fastapi import Depends
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy.orm import Session

from wacruit.src.apps.seminar.models import Seminar
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class SeminarRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_seminar_by_id(self, seminar_id: int) -> Seminar | None:
        query = select(Seminar).where(Seminar.id == seminar_id)
        return self.session.execute(query).scalar()

    def get_all_seminars(self) -> list[Seminar]:
        query = select(Seminar)
        return list(self.session.execute(query).scalars().all())

    def get_active_seminars(self) -> list[Seminar]:
        query = select(Seminar).where(Seminar.is_active == true())
        return list(self.session.execute(query).scalars().all())

    def create_seminar(self, seminar: Seminar) -> Seminar:
        with self.transaction:
            self.session.add(seminar)
        return seminar

    def update_seminar(self, seminar: Seminar) -> Seminar:
        with self.transaction:
            self.session.merge(seminar)
        return seminar
