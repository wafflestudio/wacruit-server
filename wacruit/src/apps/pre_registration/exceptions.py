from wacruit.src.apps.common.exceptions import WacruitException


class PreRegistNotActiveException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="활성화된 사전 알림이 존재하지 않습니다.")


class PreRegistNotExistException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="해당하는 사전 알림이 존재하지 않습니다.")


class PreRegistAlreadyExistException(WacruitException):
    def __init__(self):
        super().__init__(status_code=409, detail="활성화된 사전 알림이 이미 존재합니다.")
