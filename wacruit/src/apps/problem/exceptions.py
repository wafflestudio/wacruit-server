from fastapi import HTTPException


class ProblemNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="존재하지 않는 문제입니다.")
