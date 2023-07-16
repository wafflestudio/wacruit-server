from fastapi import HTTPException


class ProblemNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(404, "존재하지 않는 문제입니다.")
