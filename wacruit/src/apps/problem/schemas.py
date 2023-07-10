from typing import Any, Literal

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.judge.schemas import JudgeSubmissionStatusModel


class ProblemResponse(BaseModel):
    problem_num: int
    body: str


class CodeSubmitRequest(BaseModel):
    problem_id: int
    language: Language = Field(...)
    source_code: str = Field(..., max_length=10000)
    is_test: bool = Field(False)
    testcases: list[Any] | None = Field(None, max_items=10)


class CodeSubmissionResult(BaseModel):
    id: int
    status: JudgeSubmissionStatusModel
    result: str


class CodeSubmissionResultResponse(BaseModel):
    results: list[CodeSubmissionResult]
