from enum import StrEnum

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
    INTERNAL_ERROR = "INTERNAL_ERROR"

    def to_submission_result_status(self) -> CodeSubmissionResultStatus:
        status_map = {
            HoduSubmitStatus.CORRECT: CodeSubmissionResultStatus.CORRECT,
            HoduSubmitStatus.WRONG: CodeSubmissionResultStatus.WRONG,
            HoduSubmitStatus.COMPILE_ERROR: CodeSubmissionResultStatus.COMPILE_ERROR,
            HoduSubmitStatus.RUNTIME_ERROR: CodeSubmissionResultStatus.RUNTIME_ERROR,
            HoduSubmitStatus.TIME_LIMIT_EXCEEDED: (
                CodeSubmissionResultStatus.TIME_LIMIT_EXCEEDED
            ),
            HoduSubmitStatus.MEMORY_LIMIT_EXCEEDED: (
                CodeSubmissionResultStatus.MEMORY_LIMIT_EXCEEDED
            ),
            HoduSubmitStatus.INTERNAL_ERROR: (
                CodeSubmissionResultStatus.INTERNAL_SERVER_ERROR
            ),
        }
        return status_map[self]

    @staticmethod
    def from_submission_result_status(
        status: CodeSubmissionResultStatus,
    ) -> "HoduSubmitStatus":
        status_map = {
            CodeSubmissionResultStatus.CORRECT: HoduSubmitStatus.CORRECT,
            CodeSubmissionResultStatus.WRONG: HoduSubmitStatus.WRONG,
            CodeSubmissionResultStatus.COMPILE_ERROR: HoduSubmitStatus.COMPILE_ERROR,
            CodeSubmissionResultStatus.RUNTIME_ERROR: HoduSubmitStatus.RUNTIME_ERROR,
            CodeSubmissionResultStatus.TIME_LIMIT_EXCEEDED: (
                HoduSubmitStatus.TIME_LIMIT_EXCEEDED
            ),
            CodeSubmissionResultStatus.MEMORY_LIMIT_EXCEEDED: (
                HoduSubmitStatus.MEMORY_LIMIT_EXCEEDED
            ),
            CodeSubmissionResultStatus.INTERNAL_SERVER_ERROR: (
                HoduSubmitStatus.INTERNAL_ERROR
            ),
        }
        try:
            return status_map[status]
        except KeyError as exc:
            raise ValueError(f"Invalid CodeSubmissionResultStatus: {status}") from exc


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
