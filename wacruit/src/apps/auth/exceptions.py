from wacruit.src.apps.common.exceptions import WacruitException


class UserNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="해당하는 계정이 존재하지 않습니다.")


class InvalidTokenException(WacruitException):
    def __init__(self):
        super().__init__(status_code=401, detail="잘못된 토큰입니다.")
