from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import CodeSubmissionResultStatus
from wacruit.src.apps.common.enums import Language


class HoduLanguage(StrEnum):
    C = "c"
    CPP = "cpp"
    GO = "go"
    JAVA = "java"
    KOTLIN = "kotlin"
    NODE = "node"
    PYTHON = "python"
    RUST = "rust"
    TYPESCRIPT = "typescript"

    def to_language(self) -> Language:
        mapping = {
            HoduLanguage.C: Language.C,
            HoduLanguage.CPP: Language.CPP,
            HoduLanguage.GO: Language.GO,
            HoduLanguage.JAVA: Language.JAVA,
            HoduLanguage.KOTLIN: Language.KOTLIN,
            HoduLanguage.NODE: Language.JAVASCRIPT,
            HoduLanguage.PYTHON: Language.PYTHON,
            HoduLanguage.RUST: Language.RUST,
            HoduLanguage.TYPESCRIPT: Language.TYPESCRIPT,
        }
        if self in mapping:
            return mapping[self]
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
    CORRECT = "Accepted"
    WRONG = "WrongAnswer"
    COMPILE_ERROR = "CompileError"
    RUNTIME_ERROR = "RuntimeError"
    TIME_LIMIT_EXCEEDED = "TimeLimitExceeded"
    MEMORY_LIMIT_EXCEEDED = "MemoryLimitExceeded"
    INTERNAL_ERROR = "InternalError"

    def to_submission_result_status(self) -> CodeSubmissionResultStatus:
        mapping = {
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
        return mapping[self]

    @staticmethod
    def from_submission_result_status(
        status: CodeSubmissionResultStatus,
    ) -> "HoduSubmitStatus":
        mapping = {
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
        if status in mapping:
            return mapping[status]
        raise ValueError(f"Invalid CodeSubmissionResultStatus: {status}")


class HoduSubmitExtraFields(BaseModel):
    time: float | None
    memory: int | None
    stdout: str | None
    stderr: str | None


class HoduSubmitResponse(BaseModel):
    status: HoduSubmitStatus
    fields: HoduSubmitExtraFields


class HoduSubmitErrorResponse(BaseModel):
    detail: str
