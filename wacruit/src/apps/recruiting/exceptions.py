from wacruit.src.apps.common.exceptions import WacruitException


class RecruitingNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(404, "존재하지 않는 리크루팅입니다.")


class RecruitingClosedException(WacruitException):
    def __init__(self):
        super().__init__(status_code=403, detail="모집이 마감되었습니다.")


class RecruitingNotAppliedException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="지원하지 않은 리크루팅입니다.")
