from typing import Any, Sequence

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy import Row
from sqlalchemy import select
from sqlalchemy.orm import Session

from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class RecruitingRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    # pylint: disable=not-callable
    def get_all_recruitings(self) -> Sequence[Row]:
        query = select(
            func.max(Recruiting.id).label("id"),
            func.max(Recruiting.name).label("name"),
            func.max(Recruiting.is_active).label("is_active"),
            func.max(Recruiting.from_date).label("from_date"),
            func.max(Recruiting.to_date).label("to_date"),
            func.count(ResumeSubmission.id).label("applicant_count"),
        ).join(ResumeSubmission)
        print("\n", query)
        return self.session.execute(query).all()
