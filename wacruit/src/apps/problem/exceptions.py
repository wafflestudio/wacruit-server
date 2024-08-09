from wacruit.src.apps.common.exceptions import WacruitException
from wacruit.src.apps.judge.schemas import JudgeGetSubmissionResponse


class ProblemNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 문제입니다.")


class CodeSubmissionFailedException(WacruitException):
    def __init__(self):
        super().__init__(status_code=400, detail="코드 제출에 실패하였습니다.")


class CodeSubmissionErrorException(WacruitException):
    message: str

    def __init__(self, code_submission_result: JudgeGetSubmissionResponse):
        self.message = code_submission_result.message or ""
        super().__init__(
            status_code=500,
            detail="불편을 드려 죄송합니다.\n"
            "코드 제출 중 오류가 발생하였습니다. 다시 시도해주세요.\n"
            "지속적으로 문제가 발생하면 관리자에게 문의 부탁드립니다.",
        )

    def __str__(self):
        return f"{super().__str__()} {self.message}"


class TestcaseNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="테스트케이스를 찾을 수 없습니다.\n지속적으로 문제가 발생하면 관리자에게 문의 부탁드립니다.",
        )


class NoRecentSubmissionException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="최근 제출한 코드가 없습니다.")
