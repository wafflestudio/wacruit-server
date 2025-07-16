from wacruit.src.apps.common.exceptions import WacruitException


class QuestionNowFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 질문입니다.")


class QuestionListEmptyException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="질문 리스트가 비어 있습니다.")
