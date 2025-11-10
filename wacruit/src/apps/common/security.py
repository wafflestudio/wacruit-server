from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from wacruit.src.secrets import AWSSecretManager
from wacruit.src.settings import settings


@cache
def get_token_secret() -> str:
    secret_manager = AWSSecretManager()
    if secret_manager.is_available():
        secret_token = secret_manager.get_secret("token_secret")
    else:
        secret_token = settings.TOKEN_SECRET
    return secret_token


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
