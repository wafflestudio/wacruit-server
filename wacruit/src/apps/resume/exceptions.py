from wacruit.src.apps.common.exceptions import WacruitException


class ResumeNotFound(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 제출입니다.")


class QuestionNotFound(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 질문입니다.")


class RecruitingNotFound(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 지원서입니다.")
