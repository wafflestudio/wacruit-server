from fastapi import HTTPException

class MemberNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Member not found."
        )

class MemberAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Member already exists."
        )
