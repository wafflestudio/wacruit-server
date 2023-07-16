from typing import Any

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.common.schemas import OrmModel
from wacruit.src.apps.judge.schemas import JudgeSubmissionStatusModel


class TestCaseResponse(OrmModel):
    stdin: str
    expected_output: str


class ProblemResponse(OrmModel):
    num: int
    body: str
    testcases: list[TestCaseResponse]


class CodeSubmitRequest(BaseModel):
    problem_id: int
    language: Language = Field(...)
    source_code: str = Field(..., max_length=10000)
    is_test: bool = Field(False)
    extra_testcases: list[TestCaseResponse] | None = Field(None, max_items=10)


class CodeSubmissionResult(BaseModel):
    id: int
    status: str
    msg: str | None
    stdout: str | None
    time: float | None
    memory: int | None
