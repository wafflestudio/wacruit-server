from wacruit.src.apps.common.exceptions import WacruitException


class HistoryNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="History key not found")
