from datetime import datetime
from typing import Literal, TYPE_CHECKING

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
    status: CodeSubmissionStatus | Literal[0]  # 0 means NOT_SUBMITTED


class RecruitingResponse(OrmModel):
    name: str
    is_active: bool
    from_date: datetime
    to_date: datetime
    description: str
    problem_status: list[ProblemStatusDto]
