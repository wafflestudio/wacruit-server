from wacruit.src.apps.common.exceptions import WacruitException


class ProblemNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 문제입니다.")
