from wacruit.src.apps.common.exceptions import WacruitException


class UserNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="해당하는 계정이 존재하지 않습니다.")


class InvalidTokenException(WacruitException):
    def __init__(self):
        super().__init__(status_code=401, detail="잘못된 토큰입니다.")


class EmailConflictException(WacruitException):
    def __init__(self):
        super().__init__(status_code=409, detail="이미 존재하는 이메일입니다.")


class InvalidPasswordResetCodeException(WacruitException):
    def __init__(self):
        super().__init__(status_code=400, detail="인증 번호가 올바르지 않습니다.")


class ExpiredPasswordResetCodeException(WacruitException):
    def __init__(self):
        super().__init__(status_code=400, detail="만료된 인증 번호입니다.")


class PasswordResetCodeNotVerifiedException(WacruitException):
    def __init__(self):
        super().__init__(status_code=400, detail="인증 번호 확인이 필요합니다.")
