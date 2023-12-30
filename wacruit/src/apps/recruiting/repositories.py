from typing import Sequence

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import Session

from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.models import RecruitingApplication
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
    def get_all_recruitings(self) -> Sequence[Recruiting]:
        query = select(Recruiting)
        return self.session.execute(query).scalars().all()

    def get_rookie_applicant_count(self, recruiting_id: int) -> int:
        query = (
            select(func.count(CodeSubmission.user_id.distinct()))
            .select_from(Recruiting)
            .outerjoin(Problem, Problem.recruiting_id == Recruiting.id)
            .outerjoin(CodeSubmission, CodeSubmission.problem_id == Problem.id)
            .where(Recruiting.id == recruiting_id)
        )
        return self.session.execute(query).scalar_one()

    def get_recruiting_by_id(self, recruiting_id: int) -> Recruiting | None:
        query = select(Recruiting).where(Recruiting.id == recruiting_id)
        return self.session.execute(query).scalar_one()

    def get_recruiting_with_code_submission_status_by_id(
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
            .order_by(CodeSubmission.created_at.desc())
            .options(
                contains_eager(Recruiting.problems).contains_eager(Problem.submissions)
            )
        )
        return self.session.execute(query).scalars().first()

    def get_recruiting_result_by_id(
        self, recruiting_id: int, user_id: int
    ) -> RecruitingApplication | None:
        query = (
            select(RecruitingApplication)
            .where(RecruitingApplication.recruiting_id == recruiting_id)
            .where(RecruitingApplication.user_id == user_id)
        )
        return self.session.execute(query).scalar()
