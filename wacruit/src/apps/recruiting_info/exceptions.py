from wacruit.src.apps.common.exceptions import WacruitException


class RecruitingInfoAlreadyExistsException(WacruitException):
    def __init__(self):
        super().__init__(status_code=409, detail="이미 존재하는 RecruitingInfo입니다.")
