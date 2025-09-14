from fastapi import Depends
from sqlalchemy.orm import Session

from wacruit.src.apps.common.enums import Position
from wacruit.src.apps.member.models import Member
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class MemberRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ) -> None:
        self.session = session
        self.transaction = transaction

    def get_member_by_id(self, member_id: int) -> Member | None:
        return self.session.query(Member).filter(Member.id == member_id).first()

    def create_member(self, member: Member) -> Member:
        with self.transaction:
            self.session.add(member)
        return member

    def get_all_members(
        self, position: Position | None, offset: int, limit: int
    ) -> list[Member]:
        query = self.session.query(Member)

        if position is not None:
            query = query.where(Member.position == position)

        members = query.offset(offset).limit(limit).all()

        return members

    def update_member(self, member: Member) -> Member:
        with self.transaction:
            self.session.merge(member)
        return member
