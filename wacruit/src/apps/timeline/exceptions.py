from wacruit.src.apps.common.exceptions import WacruitException


class TimelineCategoryNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="타임라인 카테고리를 찾을 수 없습니다.")


class TimelineNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="타임라인을 찾을 수 없습니다.")
