from wacruit.src.apps.common.exceptions import WacruitException


class MailConfigException(WacruitException):
    def __init__(self):
        super().__init__(status_code=500, detail="메일 설정이 올바르지 않습니다.")


class MailSendFailedException(WacruitException):
    def __init__(self):
        super().__init__(status_code=502, detail="메일 전송에 실패했습니다.")
