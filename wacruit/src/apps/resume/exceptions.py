from wacruit.src.apps.common.exceptions import WacruitException


class ResumeNotFound(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 답변입니다.")


class QuestionNotFound(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 질문입니다.")


class RecruitingNotFound(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 전형입니다.")
