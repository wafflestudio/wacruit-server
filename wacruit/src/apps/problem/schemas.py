from typing import Any, Literal

from pydantic import BaseModel
from pydantic import Field

SupportedLanguage = Literal[
    "C", "CPP", "JAVA", "KOTLIN", "SCALA", "SWIFT", "JAVASCRIPT", "TYPESCRIPT", "PYTHON"
]

TestCaseState = Literal["RUNNING", "SUCCESS", "FAILED"]


class ProblemResponse(BaseModel):
    problem_num: int
    body: str


class CodeSubmitRequest(BaseModel):
    problem_id: int
    language: SupportedLanguage = Field(...)
    source_code: str = Field(..., max_length=10000)
    is_test: bool = Field(False)
    testcases: list[Any] | None = Field(None, max_items=10)


class TestCaseResult(BaseModel):
    id: int
    # state: TestCaseState
    result: str


class CodeSubmissionResultResponse(BaseModel):
    results: list[TestCaseResult]
