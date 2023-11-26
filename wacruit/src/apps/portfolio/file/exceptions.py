from wacruit.src.apps.common.exceptions import WacruitException


class NumPortfolioLimitException(WacruitException):
    def __init__(self):
        super().__init__(status_code=403, detail="포트폴리오는 최대 1개까지 업로드 가능합니다.")


class PortfolioNotFoundException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="포트폴리오를 찾을 수 없습니다.")


class InValidGenerationException(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="유효하지 않은 기수입니다.")
