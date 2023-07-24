from typing import Sequence

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy import Row
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import Session

from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
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
        query = (
            select(
                Recruiting.id.label("id"),
                Recruiting.name.label("name"),
                Recruiting.is_active.label("is_active"),
                Recruiting.from_date.label("from_date"),
                Recruiting.to_date.label("to_date"),
                func.count(ResumeSubmission.user_id.distinct()).label(
                    "applicant_count"
                ),
            )
            .outerjoin(ResumeSubmission)
            .group_by(
                Recruiting.id,
                Recruiting.name,
                Recruiting.is_active,
                Recruiting.from_date,
                Recruiting.to_date,
            )
        )
        return self.session.execute(query).all()

    def get_recruiting_by_id(
        self, recruiting_id: int, user_id: int
    ) -> Recruiting | None:
        query = (
            select(Recruiting)
            .outerjoin(Problem, Problem.recruiting_id == recruiting_id)
            .outerjoin(
                CodeSubmission,
                (CodeSubmission.problem_id == Problem.id)
                & (CodeSubmission.user_id == user_id),
            )
            .where(Recruiting.id == recruiting_id)
            .order_by(CodeSubmission.create_at.desc())
            .options(
                contains_eager(Recruiting.problems).contains_eager(Problem.submissions)
            )
        )
        return self.session.execute(query).scalars().first()
