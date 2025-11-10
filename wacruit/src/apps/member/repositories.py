from fastapi import Depends
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import Float
from sqlalchemy import null
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
        # generation을 숫자로 캐스트하여 내림차순 정렬, NULL은 뒤로 보내기
        safe_num = case(
            (
                Member.generation.op("~")("^[0-9]+(\\.[0-9]+)?$"),
                cast(Member.generation, Float),
            ),
            else_=null(),
        )

        # ANDROID, IOS, FRONTEND, BACKEND, DESIGNER 순서로 정렬
        position_order = case(
            (Member.position == Position.ANDROID, 1),
            (Member.position == Position.IOS, 2),
            (Member.position == Position.FRONTEND, 3),
            (Member.position == Position.BACKEND, 4),
            (Member.position == Position.DESIGNER, 5),
            else_=6,
        )

        query = self.session.query(Member).order_by(
            safe_num.desc().nulls_last(), position_order.asc()
        )

        if position is not None:
            query = query.where(Member.position == position)

        members = query.offset(offset).limit(limit).all()

        return members

    def update_member(self, member: Member) -> Member:
        with self.transaction:
            self.session.merge(member)
        return member
