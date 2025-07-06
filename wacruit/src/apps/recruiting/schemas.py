from datetime import datetime
from typing import Literal, TYPE_CHECKING

from pydantic import BaseModel

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import RecruitingApplicationStatus
from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.schemas import OrmModel
from wacruit.src.apps.problem.schemas_v2 import ProblemCreateDto
from wacruit.src.apps.resume.schemas import ResumeQuestionCreateDto

if TYPE_CHECKING:
    from wacruit.src.apps.problem.models import Problem


class RecruitingSummaryResponse(OrmModel):
    id: int
    name: str
    type: RecruitingType
    is_active: bool
    from_date: datetime | None
    to_date: datetime | None
    applicant_count: int
    short_description: str


class ProblemStatusDto(OrmModel):
    id: int
    num: int
    status: CodeSubmissionStatus | Literal[0]  # 0 means NOT_SUBMITTED


# 기존에 존재하던 RecruitingResponse을 UserRecruitingResponse로 변경


class UserRecruitingResponse(OrmModel):
    id: int
    name: str
    type: RecruitingType
    is_active: bool
    applied: bool
    from_date: datetime | None
    to_date: datetime | None
    description: str
    problem_status: list[ProblemStatusDto]


class RecruitingResponse(OrmModel):
    id: int
    name: str
    generation: str
    type: RecruitingType
    is_active: bool
    from_date: datetime | None
    to_date: datetime | None
    short_description: str | None = None
    description: str
    resume_questions: list[ResumeQuestionCreateDto]
    problems: list[ProblemCreateDto] | None = None

    @classmethod
    def from_orm(cls, obj):
        resume_questions = [
            ResumeQuestionCreateDto.from_orm(question)
            for question in obj.resume_questions
        ]
        problems = (
            [ProblemCreateDto.from_orm(problem) for problem in obj.problems]
            if obj.problems
            else None
        )
        return cls(
            id=obj.id,
            name=obj.name,
            generation=obj.generation,
            type=obj.type,
            is_active=obj.is_active,
            from_date=obj.from_date,
            to_date=obj.to_date,
            short_description=obj.short_description,
            description=obj.description,
            resume_questions=resume_questions,
            problems=problems,
        )


class RecruitingResultResponse(BaseModel):
    status: RecruitingApplicationStatus


class RecruitingCreateRequest(BaseModel):
    name: str
    type: str
    generation: str
    is_active: bool
    from_date: datetime
    to_date: datetime
    short_description: str | None = None
    description: str
    resume_questions: list[ResumeQuestionCreateDto]
    problems: list[ProblemCreateDto] | None = None


class RecruitingUpdateRequest(BaseModel):
    name: str | None = None
    type: RecruitingType | None = None
    generation: str | None = None
    is_active: bool | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    short_description: str | None = None
    description: str | None = None
    resume_questions: list[ResumeQuestionCreateDto] | None = None
    problems: list[ProblemCreateDto] | None = None


class RecruitingInfoResponse(OrmModel):
    id: int
    type: str
    info_num: int
    title: str
    date_info: datetime
