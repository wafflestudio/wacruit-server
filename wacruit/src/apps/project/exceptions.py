from wacruit.src.apps.common.exceptions import WacruitException


class ProjectNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 프로젝트입니다.")


class ProjectAlreadyExistsException(WacruitException):
    def __init__(self):
        super().__init__(status_code=409, detail="이미 존재하는 프로젝트입니다.")


class ProjectImageNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 프로젝트 이미지입니다.")


class GetPresignedURLException(WacruitException):
    def __init__(self):
        super().__init__(
            status_code=500, detail="프로젝트 이미지의 presigned URL을 가져오는데 실패했습니다."
        )
