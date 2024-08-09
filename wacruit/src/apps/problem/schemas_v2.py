from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.schemas import OrmModel
from wacruit.src.apps.hodu.schemas import HoduLanguage
from wacruit.src.apps.hodu.schemas import HoduSubmitStatus


class TestcaseDto(OrmModel):
    stdin: str
    expected_output: str


class ProblemResponse(OrmModel):
    id: int
    num: int
    body: str
    testcases: list[TestcaseDto]


class CodeSubmitRequest(BaseModel):
    problem_id: int
    language: HoduLanguage = Field(...)
    source_code: str = Field(..., max_length=100000)
    is_example: bool = Field(False)
    extra_testcases: list[TestcaseDto] = Field([], max_items=10)


class CodeSubmissionResultResponse(BaseModel):
    num: int
    status: HoduSubmitStatus
    stdout: str | None = None
    time: float | None = None
    memory: float | None = None


TokenStr = str
