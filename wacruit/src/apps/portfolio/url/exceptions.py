from wacruit.src.apps.common.exceptions import WacruitException


class NumPortfolioUrlLimitException(WacruitException):
    def __init__(self):
        super().__init__(status_code=403, detail="등록 가능한 Url 개수 한계를 초과하셨습니다.")


class PortfolioUrlNotAuthorized(WacruitException):
    def __init__(self):
        super().__init__(status_code=403, detail="권한이 없습니다.")


class PortfolioUrlNotFound(WacruitException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 URL입니다.")
