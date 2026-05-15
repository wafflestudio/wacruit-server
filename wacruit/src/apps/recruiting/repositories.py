from typing import Sequence

from fastapi import Depends
from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager

from wacruit.src.apps.common.enums import CodeSubmissionResultStatus
from wacruit.src.apps.common.enums import RecruitingApplicationStatus
from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import CodeSubmissionResult
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.recruiting.exceptions import RecruitingAlreadyAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingClosedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.models import RecruitingApplication
from wacruit.src.apps.recruiting_info.models import RecruitingInfo
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.user.models import User
from wacruit.src.database.connection import Transaction
from wacruit.src.database.connection import get_db_session


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

    def get_recruiting_infos_by_type(
        self, recruiting_type: RecruitingType
    ) -> Sequence[RecruitingInfo] | None:
        # 먼저 해당 타입에서 to_date가 가장 큰 recruiting_id를 찾습니다
        latest_recruiting_subquery = (
            select(Recruiting.id)
            .where(Recruiting.type == recruiting_type)
            .order_by(Recruiting.to_date.desc())
            .limit(1)
        ).scalar_subquery()

        query = (
            select(RecruitingInfo)
            .where(RecruitingInfo.recruiting_id == latest_recruiting_subquery)
            .order_by(RecruitingInfo.info_num.asc())
        )
        return self.session.execute(query).scalars().all()

    def get_recruiting_info_by_info_num(
        self, info_num: int, recruiting_id: int
    ) -> RecruitingInfo | None:
        query = select(RecruitingInfo).where(
            RecruitingInfo.info_num == info_num,
            RecruitingInfo.recruiting_id == recruiting_id,
        )
        return self.session.execute(query).scalar()

    def create_recruiting(self, recruiting: Recruiting) -> Recruiting:
        with self.transaction:
            self.session.add(recruiting)
            self.session.flush()
        return recruiting

    def update_recruiting(self, recruiting: Recruiting) -> Recruiting:
        with self.transaction:
            self.session.merge(recruiting)
            self.session.flush()
        return recruiting

    def create_recruiting_info(self, recruiting_info: RecruitingInfo):
        with self.transaction:
            self.session.add(recruiting_info)
            self.session.flush()
        return recruiting_info

    def get_recruiting_info_by_id(
        self, recruiting_info_id: int
    ) -> RecruitingInfo | None:
        query = select(RecruitingInfo).where(RecruitingInfo.id == recruiting_info_id)
        return self.session.execute(query).scalar()

    def update_recruiting_info(self, recruiting_info: RecruitingInfo) -> RecruitingInfo:
        with self.transaction:
            self.session.merge(recruiting_info)
            self.session.flush()
        return recruiting_info

    def get_submissions_by_recruiting_id(
        self, recruiting_id: int, limit: int, offset: int
    ):
        question_ids = (
            self.session.execute(
                select(ResumeQuestion.id)
                .where(ResumeQuestion.recruiting_id == recruiting_id)
                .order_by(ResumeQuestion.question_num)
            )
            .scalars()
            .all()
        )

        q1_id = question_ids[0]
        q2_id = question_ids[1]
        q3_id = question_ids[2]

        problem_ids = (
            self.session.execute(
                select(Problem.id)
                .where(Problem.recruiting_id == recruiting_id)
                .order_by(Problem.num)
            )
            .scalars()
            .all()
        )

        p1_id = problem_ids[0]
        p2_id = problem_ids[1]
        p3_id = problem_ids[2]

        resume_max_time = (
            select(
                ResumeSubmission.user_id,
                ResumeSubmission.question_id,
                func.max(ResumeSubmission.created_at).label("max_time"),
            )
            .where(ResumeSubmission.question_id.in_([q1_id, q2_id, q3_id]))
            .group_by(ResumeSubmission.user_id, ResumeSubmission.question_id)
            .subquery("resume_max_time")
        )

        resume_latest = (
            select(
                ResumeSubmission.user_id,
                ResumeSubmission.question_id,
                ResumeSubmission.answer,
            )
            .join(
                resume_max_time,
                (ResumeSubmission.user_id == resume_max_time.c.user_id)
                & (ResumeSubmission.question_id == resume_max_time.c.question_id)
                & (ResumeSubmission.created_at == resume_max_time.c.max_time),
            )
            .subquery("resume_latest")
        )

        resume_pivot = (
            select(
                resume_latest.c.user_id,
                func.max(
                    case((resume_latest.c.question_id == q1_id, resume_latest.c.answer))
                ).label("q1_answer"),
                func.max(
                    case((resume_latest.c.question_id == q2_id, resume_latest.c.answer))
                ).label("q2_answer"),
                func.max(
                    case((resume_latest.c.question_id == q3_id, resume_latest.c.answer))
                ).label("q3_answer"),
            )
            .group_by(resume_latest.c.user_id)
            .subquery("resume_pivot")
        )

        code_max_time = (
            select(
                CodeSubmission.user_id,
                CodeSubmission.problem_id,
                func.max(CodeSubmission.created_at).label("max_time"),
            )
            .where(CodeSubmission.problem_id.in_([p1_id, p2_id, p3_id]))
            .group_by(CodeSubmission.user_id, CodeSubmission.problem_id)
            .subquery("code_max_time")
        )

        latest_code = (
            select(CodeSubmission.id, CodeSubmission.user_id, CodeSubmission.problem_id)
            .join(
                code_max_time,
                (CodeSubmission.user_id == code_max_time.c.user_id)
                & (CodeSubmission.problem_id == code_max_time.c.problem_id)
                & (CodeSubmission.created_at == code_max_time.c.max_time),
            )
            .subquery("latest_code")
        )

        code_result_join = (
            select(
                latest_code.c.user_id,
                latest_code.c.problem_id,
                func.count(CodeSubmissionResult.testcase_id).label("correct_count"),
            )
            .join(
                CodeSubmissionResult,
                CodeSubmissionResult.submission_id == latest_code.c.id,
            )
            .where(CodeSubmissionResult.status == CodeSubmissionResultStatus.CORRECT)
            .group_by(latest_code.c.user_id, latest_code.c.problem_id)
            .subquery("code_result_join")
        )

        code_pivot = (
            select(
                code_result_join.c.user_id,
                func.coalesce(
                    func.max(
                        case(
                            (
                                code_result_join.c.problem_id == p1_id,
                                code_result_join.c.correct_count,
                            )
                        )
                    ),
                    0,
                ).label("problem_1_correct"),
                func.coalesce(
                    func.max(
                        case(
                            (
                                code_result_join.c.problem_id == p2_id,
                                code_result_join.c.correct_count,
                            )
                        )
                    ),
                    0,
                ).label("problem_2_correct"),
                func.coalesce(
                    func.max(
                        case(
                            (
                                code_result_join.c.problem_id == p3_id,
                                code_result_join.c.correct_count,
                            )
                        )
                    ),
                    0,
                ).label("problem_3_correct"),
            )
            .group_by(code_result_join.c.user_id)
            .subquery("code_pivot")
        )

        stmt = (
            select(
                User.first_name,
                User.last_name,
                User.university,
                User.college,
                User.department,
                User.phone_number,
                User.github_email,
                User.slack_email,
                User.notion_email,
                resume_pivot.c.q1_answer,
                resume_pivot.c.q2_answer,
                resume_pivot.c.q3_answer,
                func.coalesce(code_pivot.c.problem_1_correct, 0).label(
                    "problem_1_correct"
                ),
                func.coalesce(code_pivot.c.problem_2_correct, 0).label(
                    "problem_2_correct"
                ),
                func.coalesce(code_pivot.c.problem_3_correct, 0).label(
                    "problem_3_correct"
                ),
            )
            .join(RecruitingApplication, RecruitingApplication.user_id == User.id)
            .outerjoin(resume_pivot, resume_pivot.c.user_id == User.id)
            .outerjoin(code_pivot, code_pivot.c.user_id == User.id)
            .where(RecruitingApplication.recruiting_id == recruiting_id)
            .order_by(RecruitingApplication.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = self.session.execute(stmt).mappings().all()
        return result
