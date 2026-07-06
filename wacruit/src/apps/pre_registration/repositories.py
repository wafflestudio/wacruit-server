from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy.orm import Session

from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.apps.pre_registration.models import PreRegistrationUser
from wacruit.src.database.connection import Transaction
from wacruit.src.database.connection import get_db_session


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
        with self.transaction:
            self.session.execute(
                delete(PreRegistration).where(PreRegistration.id == pre_registration_id)
            )

    def create_pre_registration_user(
        self, pre_registration_user: PreRegistrationUser
    ) -> PreRegistrationUser:
        with self.transaction:
            self.session.add(pre_registration_user)
        return pre_registration_user

    def count_pre_registration_users(
        self,
        pre_registration_id: int | None,
        active_only: bool,
    ) -> int:
        query = (
            select(func.count()).select_from(PreRegistrationUser).join(PreRegistration)
        )
        if pre_registration_id is not None:
            query = query.where(
                PreRegistrationUser.pre_registration_id == pre_registration_id
            )
        if active_only:
            query = query.where(PreRegistration.is_active == true())
        return int(self.session.execute(query).scalar_one())

    def get_pre_registration_users(
        self,
        pre_registration_id: int | None,
        active_only: bool,
        limit: int | None,
        offset: int,
    ) -> list[PreRegistrationUser]:
        query = select(PreRegistrationUser).join(PreRegistration)
        if pre_registration_id is not None:
            query = query.where(
                PreRegistrationUser.pre_registration_id == pre_registration_id
            )
        if active_only:
            query = query.where(PreRegistration.is_active == true())
        query = query.order_by(PreRegistrationUser.id.desc()).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return list(self.session.execute(query).scalars())
