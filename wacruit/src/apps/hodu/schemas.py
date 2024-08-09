from enum import StrEnum
from subprocess import STDOUT
from typing import Self

from MySQLdb import TIME
from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import CodeSubmissionResultStatus
from wacruit.src.apps.common.enums import Language


class HoduLanguage(StrEnum):
    C = "c"
    CPP = "c++"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    # KOTLIN = "kotlin"
    # SWIFT = "swift"

    def to_language(self) -> Language:
        match self:
            case HoduLanguage.C:
                return Language.C
            case HoduLanguage.CPP:
                return Language.CPP
            case HoduLanguage.JAVA:
                return Language.JAVA
            case HoduLanguage.JAVASCRIPT:
                return Language.JAVASCRIPT
            case HoduLanguage.PYTHON:
                return Language.PYTHON
            # case HoduLanguage.KOTLIN:
            #     return Language.KOTLIN
            # case HoduLanguage.SWIFT:
            #     return Language.SWIFT
            case _:
                raise ValueError(f"Invalid HoduLanguage: {self}")


class HoduField(StrEnum):
    WILDCARD = "*"
    STDOUT = "stdout"
    STDERR = "stderr"
    TIME = "time"
    MEMORY = "memory"


class HoduSubmitRequest(BaseModel):
    language: HoduLanguage = Field(...)
    code: str = Field(..., max_length=100000)
    stdin: str
    expected_stdout: str
    time_limit: float = Field(5.0)  # seconds
    memory_limit: int = Field(256 * 1024)  # KB
    fields: list[HoduField] = Field([])


class HoduSubmitStatus(StrEnum):
    CORRECT = "CORRECT"
    WRONG = "WRONG"
    COMPILE_ERROR = "COMPILE_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"

    def to_submission_result_status(self):
        match self:
            case HoduSubmitStatus.CORRECT:
                return CodeSubmissionResultStatus.CORRECT
            case HoduSubmitStatus.WRONG:
                return CodeSubmissionResultStatus.WRONG
            case HoduSubmitStatus.COMPILE_ERROR:
                return CodeSubmissionResultStatus.COMPILE_ERROR
            case HoduSubmitStatus.RUNTIME_ERROR:
                return CodeSubmissionResultStatus.RUNTIME_ERROR
            case HoduSubmitStatus.TIME_LIMIT_EXCEEDED:
                return CodeSubmissionResultStatus.TIME_LIMIT_EXCEEDED
            case HoduSubmitStatus.MEMORY_LIMIT_EXCEEDED:
                return CodeSubmissionResultStatus.MEMORY_LIMIT_EXCEEDED

    @staticmethod
    def from_submission_result_status(
        status: CodeSubmissionResultStatus,
    ) -> "HoduSubmitStatus":
        match status:
            case CodeSubmissionResultStatus.CORRECT:
                return HoduSubmitStatus.CORRECT
            case CodeSubmissionResultStatus.WRONG:
                return HoduSubmitStatus.WRONG
            case CodeSubmissionResultStatus.COMPILE_ERROR:
                return HoduSubmitStatus.COMPILE_ERROR
            case CodeSubmissionResultStatus.RUNTIME_ERROR:
                return HoduSubmitStatus.RUNTIME_ERROR
            case CodeSubmissionResultStatus.TIME_LIMIT_EXCEEDED:
                return HoduSubmitStatus.TIME_LIMIT_EXCEEDED
            case CodeSubmissionResultStatus.MEMORY_LIMIT_EXCEEDED:
                return HoduSubmitStatus.MEMORY_LIMIT_EXCEEDED
            case _:
                raise ValueError(f"Invalid CodeSubmissionResultStatus: {status}")


class HoduSubmitExtraFields(BaseModel):
    time: float | None
    memory: int | None
    stdout: str | None
    stderr: str | None


class HoduSubmitResponse(BaseModel):
    status: HoduSubmitStatus
    fields: HoduSubmitExtraFields


class HoduSubmitError(StrEnum):
    PAYLOAD_PARSE_ERROR = "PAYLOAD_PARSE_ERROR"
    HODU_CORE_ERROR = "HODU_CORE_ERROR"


class HoduSubmitErrorResponse(BaseModel):
    detail: HoduSubmitError
