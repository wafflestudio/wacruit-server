from fastapi import Depends
from sqlalchemy.orm import Session

from wacruit.src.apps.sponsor.models import Sponsor
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


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
    
    def get_sponsor_by_id(self, sponsor_id: str) -> Sponsor | None:
        return self.session.query(Sponsor).filter(Sponsor.id == sponsor_id).first()
    
    def get_all_sponsors(self) -> list[Sponsor]:
        return self.session.query(Sponsor).all()
    
    def update_sponsor(self, sponsor: Sponsor):
        with self.transaction:
            self.session.merge(sponsor)
        return sponsor