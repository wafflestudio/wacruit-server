from typing import Any

from fastapi import HTTPException


class WacruitException(HTTPException):
    def __init__(self, status_code: int = 0, detail: str = ""):
        assert status_code != 0, "status_code must be set"
        super().__init__(status_code=status_code, detail=detail)

    def to_response(self) -> dict[int | str, dict[str, Any]]:
        example = {
            "detail": self.detail,
        }
        return {
            self.status_code: {
                "description": self.__class__.__name__,
                "content": {
                    "application/json": {
                        "example": example,
                    },
                },
            },
        }


class ApiDeprecatedException(WacruitException):
    def __init__(self):
        super().__init__(status_code=410, detail="API Deprecated")


def responses_from(
    *exceptions: type[WacruitException],
) -> dict[int | str, dict[str, Any]]:
    responses = {}
    for exc in exceptions:
        responses.update(exc().to_response())
    return responses


class InvalidRecruitTypeException(WacruitException):
    def __init__(self, type: str):
        super().__init__(status_code=400, detail=f"Invalid recruiting type: {type}")


class InvalidProjectTypeException(WacruitException):
    def __init__(self, type: str):
        super().__init__(status_code=400, detail=f"Invalid project type: {type}")
