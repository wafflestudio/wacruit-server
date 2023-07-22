from datetime import datetime

from wacruit.src.apps.common.schemas import OrmModel


class RecruitingListResponse(OrmModel):
    id: int
    name: str
    is_active: bool
    from_date: datetime
    to_date: datetime
    applicant_count: int


class ProblemListResponse(OrmModel):
    num: int


class RecruitingResponse(OrmModel):
    name: str
    is_active: bool
    from_date: datetime
    to_date: datetime
    description: str
    problems: list[ProblemListResponse]
