from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.common.schemas import OrmModel
from wacruit.src.apps.judge.schemas import JudgeSubmissionStatusModel


class TestCaseDto(OrmModel):
    stdin: str
    expected_output: str


class ProblemResponse(OrmModel):
    num: int
    body: str
    testcases: list[TestCaseDto]


class CodeSubmitRequest(BaseModel):
    problem_id: int
    language: Language = Field(...)
    source_code: str = Field(..., max_length=10000)
    is_example: bool = Field(False)
    extra_testcases: list[TestCaseDto] | None = Field(None, max_items=10)


class CodeSubmissionResult(BaseModel):
    num: int
    status: JudgeSubmissionStatusModel
    stdout: str | None
    time: Decimal | None
    memory: Decimal | None


TokenStr = str
