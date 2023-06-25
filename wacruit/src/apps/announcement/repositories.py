from sqlite3 import IntegrityError
from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from wacruit.src.apps.announcement.models import Announcement
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class AnnouncementRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_announcements(self) -> Sequence[Announcement]:
        query = select(Announcement)
        return self.session.execute(query).scalars().all()

    def get_announcement(self, id: int) -> Announcement | None:
        query = select(Announcement).where(Announcement.id == id)
        return self.session.execute(query).scalars().first()

    def create_announcement(self, announcement: Announcement) -> Announcement:
        with self.transaction:
            self.session.add(announcement)
        return announcement

    def update_announcement(self, announcement: Announcement) -> Announcement:
        with self.transaction:
            self.session.merge(announcement)
        return announcement
