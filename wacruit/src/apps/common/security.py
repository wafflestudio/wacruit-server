from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordService:
    hasher = PasswordHasher()

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.hasher.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        try:
            return cls.hasher.verify(hashed_password, password)
        except VerifyMismatchError:
            return False
