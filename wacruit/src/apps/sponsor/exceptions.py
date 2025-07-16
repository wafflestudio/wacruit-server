from wacruit.src.apps.common.exceptions import WacruitException


class SponsorAlreadyExistsException(WacruitException):
    def __init__(self):
        super().__init__(status_code=400, detail="이미 존재하는 후원자입니다.")


class SponsorNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="후원자를 찾을 수 없습니다.")
