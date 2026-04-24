from typing import Optional
from typing import Sequence

from fastapi import Depends
from sqlalchemy import extract
from sqlalchemy import select
from sqlalchemy.orm import Session

from wacruit.src.apps.common.enums import SponsorOrder
from wacruit.src.apps.sponsor.models import Sponsor
from wacruit.src.database.connection import Transaction
from wacruit.src.database.connection import get_db_session


class SponsorRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def create_sponsor(self, sponsor: Sponsor):
        with self.transaction:
            self.session.add(sponsor)
        return sponsor

    def get_sponsor_by_sponsor_name(self, sponsor_name: str) -> Sponsor | None:
        return self.session.query(Sponsor).filter(Sponsor.name == sponsor_name).first()

    def get_sponsor_by_id(self, sponsor_id: int) -> Sponsor | None:
        return self.session.query(Sponsor).filter(Sponsor.id == sponsor_id).first()

    def get_all_sponsors(
        self, order: Optional[SponsorOrder] = None, year: Optional[int] = None
    ) -> Sequence[Sponsor]:
        stmt = select(Sponsor)

        if year is not None:
            stmt = stmt.where(extract("year", Sponsor.sponsored_date) == year)

        if order is not None:
            order_map = {
                "amount": Sponsor.amount.asc(),
                "-amount": Sponsor.amount.desc(),
                "date": Sponsor.sponsored_date.asc(),
                "-date": Sponsor.sponsored_date.desc(),
            }

            sort_condition = order_map.get(order)
            if sort_condition is not None:
                stmt = stmt.order_by(sort_condition)

        return self.session.execute(stmt).scalars().all()

    def update_sponsor(self, sponsor: Sponsor):
        with self.transaction:
            self.session.merge(sponsor)
        return sponsor
