from typing import Sequence

from alembic.util.messaging import status
from fastapi import Depends
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import Session

from wacruit.src.apps.common.enums import RecruitingApplicationStatus
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.recruiting.exceptions import RecruitingAlreadyAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingClosedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting_info.models import RecruitingInfo
from wacruit.src.apps.recruiting.models import RecruitingApplication
from wacruit.src.apps.common.enums import RecruitingType
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
        return self.session.execute(query).scalar()

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
            .outerjoin(
                RecruitingApplication,
                (RecruitingApplication.recruiting_id == recruiting_id)
                & (RecruitingApplication.user_id == user_id),
            )
            .where(Recruiting.id == recruiting_id)
            .order_by(CodeSubmission.created_at.desc())
            .options(
                contains_eager(Recruiting.problems).contains_eager(Problem.submissions),
                contains_eager(Recruiting.applicants),
            )
        )
        return self.session.execute(query).scalars().first()

    def get_recruiting_result_by_id(
        self, recruiting_id: int, user_id: int
    ) -> RecruitingApplication | None:
        query = select(RecruitingApplication).where(
            RecruitingApplication.recruiting_id == recruiting_id,
            RecruitingApplication.user_id == user_id,
        )
        return self.session.execute(query).scalar()

    def validate_recruiting_id(self, recruiting_id: int) -> None:
        recruiting = self.get_recruiting_by_id(recruiting_id)
        if recruiting is None:
            raise RecruitingNotFoundException
        if not recruiting.is_open:
            raise RecruitingClosedException

    def create_recruiting_application(
        self, recruiting_id: int, user_id: int
    ) -> RecruitingApplication:
        self.validate_recruiting_id(recruiting_id)
        if self.get_recruiting_by_id(recruiting_id) is None:
            raise RecruitingNotFoundException
        if self.get_recruiting_result_by_id(recruiting_id, user_id) is not None:
            raise RecruitingAlreadyAppliedException
        application = RecruitingApplication(
            user_id=user_id,
            recruiting_id=recruiting_id,
            status=RecruitingApplicationStatus.IN_PROGRESS,
        )
        with self.transaction:
            self.session.add(application)
        return application

    def delete_recruiting_application(
        self, recruiting_id: int, user_id: int
    ) -> RecruitingApplication:
        application = self.get_recruiting_result_by_id(recruiting_id, user_id)
        if application is None:
            raise RecruitingNotAppliedException
        with self.transaction:
            self.session.delete(application)
        return application
    
    def get_active_recruitings(self) -> Sequence[Recruiting]:
        query = (
            select(Recruiting)
            .where(Recruiting.is_active.is_(True))
            .order_by(Recruiting.from_date.desc())
        )
        return self.session.execute(query).scalars().all()
    
    def get_recruiting_info_by_type(
        self, recruiting_type: RecruitingType
    ) -> RecruitingInfo | None:
        query = (
            select(RecruitingInfo)
            .join(Recruiting, RecruitingInfo.recruiting_id == Recruiting.id)
            .where(Recruiting.type == recruiting_type)
            .order_by(RecruitingInfo.info_num.desc())
            .limit(1)
        )
        return self.session.execute(query).scalar_one_or_none()
    
    def create_recruiting(
        self, recruiting: Recruiting
    ) -> Recruiting:
        with self.transaction:
            self.session.add(recruiting)
            self.session.flush()
        return recruiting
    
    def update_recruiting(
        self, recruiting: Recruiting
    ) -> Recruiting:
        with self.transaction:
            self.session.merge(recruiting)
            self.session.flush()
        return recruiting
