from fastapi import Depends
from sqlalchemy.orm import Session

from wacruit.src.apps.member.models import Member
from wacruit.src.database.connection import get_db_session


class MemberRepository:
    def __init__(self, session: Session = Depends(get_db_session)) -> None:
        self.session = session

    def get_member_by_id(self, member_id: int) -> Member | None:
        return self.session.query(Member).filter(Member.id == member_id).first()
