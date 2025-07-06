from wacruit.src.apps.common.exceptions import WacruitException


class ProjectNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 프로젝트입니다.")


class ProjectAlreadyExistsException(WacruitException):
    def __init__(self):
        super().__init__(status_code=409, detail="이미 존재하는 프로젝트입니다.")
