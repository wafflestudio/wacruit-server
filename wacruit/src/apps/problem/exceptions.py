from wacruit.src.apps.common.exceptions import WacruitException


class ProblemNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 문제입니다.")


class CodeSubmissionFailedException(WacruitException):
    def __init__(self):
        super().__init__(status_code=400, detail="코드 제출에 실패하였습니다.")
