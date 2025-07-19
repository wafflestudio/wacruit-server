from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy.orm import Session

from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class PreRegistrationRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ) -> None:
        self.session = session
        self.transaction = transaction

    def get_pre_registration_by_id(
        self, pre_registration_id: int
    ) -> PreRegistration | None:
        query = select(PreRegistration).where(PreRegistration.id == pre_registration_id)
        return self.session.execute(query).scalar_one_or_none()

    def get_active_pre_registration(self) -> PreRegistration | None:
        query = select(PreRegistration).where(PreRegistration.is_active == true())
        return self.session.execute(query).scalar_one_or_none()

    def get_pre_registration(self) -> list[PreRegistration]:
        return list(self.session.execute(select(PreRegistration)).scalars())

    def create_pre_registration(
        self, pre_registration: PreRegistration
    ) -> PreRegistration:
        with self.transaction:
            self.session.add(pre_registration)
        return pre_registration

    def update_pre_registration(
        self, pre_registration: PreRegistration
    ) -> PreRegistration:
        with self.transaction:
            self.session.merge(pre_registration)
        return pre_registration

    def delete_pre_registration(self, pre_registration_id: int) -> None:
        self.session.execute(
            delete(PreRegistration).where(PreRegistration.id == pre_registration_id)
        )
