from wacruit.src.apps.common.exceptions import WacruitException


class SeminarNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 세미나입니다.")


class SeminarListEmptyException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="세미나 리스트가 비어있습니다.")


class SeminarNotActiveException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="활성화된 세미나가 존재하지 않습니다.")
