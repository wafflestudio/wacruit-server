from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.schemas import OrmModel
from wacruit.src.apps.hodu.schemas import HoduLanguage
from wacruit.src.apps.hodu.schemas import HoduSubmitStatus


class TestcaseDto(OrmModel):
    stdin: str
    expected_output: str

class TestCaseCreateDto(BaseModel):
    stdin: str = Field(..., max_length=10000)
    expected_output: str = Field(..., max_length=10000)
    time_limit: float = Field(..., ge=0.0)
    extra_time: float = Field(..., ge=0.0)
    memory_limit: int = Field(..., ge=0.0)
    stack_limit: int = Field(..., ge=0.0)
    is_example: bool

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

class ProblemCreateDto(BaseModel):
    num: int
    body: str
    testcases: list[TestCaseCreateDto] = Field(..., min_items = 1)

    @classmethod
    def from_orm(cls, obj) -> "ProblemCreateDto":
        testcases = [
            TestCaseCreateDto(
                stdin=testcase.stdin,
                expected_output=testcase.expected_output,
                time_limit=float(testcase.time_limit),
                extra_time=float(testcase.extra_time),
                memory_limit=testcase.memory_limit,
                stack_limit=testcase.stack_limit,
                is_example=testcase.is_example
            ) for testcase in obj.testcases
        ]
        return cls(num=obj.num, body=obj.body, testcases=testcases)

TokenStr = str
