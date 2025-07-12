from wacruit.src.apps.common.exceptions import WacruitException


class HistoryEmptyException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="History 테이블이 비어 있습니다.")
