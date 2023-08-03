from wacruit.src.apps.common.exceptions import WacruitException


class RecruitingNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(404, "존재하지 않는 리크루팅입니다.")
