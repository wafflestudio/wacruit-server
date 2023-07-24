from datetime import datetime
from typing import TYPE_CHECKING

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.schemas import OrmModel

if TYPE_CHECKING:
    from wacruit.src.apps.problem.models import Problem


class RecruitingApplicantDto(OrmModel):
    id: int
    name: str
    is_active: bool
    from_date: datetime
    to_date: datetime
    applicant_count: int


class ProblemStatusDto(OrmModel):
    num: int
    status: int

    @classmethod
    def from_orm(cls, problem: "Problem") -> "ProblemStatusDto":
        status = 0
        if problem.submissions:
            try:
                next(
                    filter(
                        lambda submission: submission.status
                        == CodeSubmissionStatus.SOLVED,
                        problem.submissions,
                    )
                )
                status = CodeSubmissionStatus.SOLVED.value
            except StopIteration:
                if problem.submissions[0].status == CodeSubmissionStatus.RUNNING:
                    status = CodeSubmissionStatus.RUNNING.value
                else:
                    status = CodeSubmissionStatus.WRONG.value

        return ProblemStatusDto(num=problem.num, status=status)


class RecruitingResponse(OrmModel):
    name: str
    is_active: bool
    from_date: datetime
    to_date: datetime
    description: str
    problems: list[ProblemStatusDto]
