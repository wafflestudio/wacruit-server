from wacruit.src.apps.common.exceptions import WacruitException


class SeminarNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 세미나입니다.")
