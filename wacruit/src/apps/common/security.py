from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings

security = HTTPBearer(scheme_name="bot_token", description="Bot Token")


@cache
def get_token_secret() -> str:
    secret_manager = OCISecretManager()
    if secret_manager.is_available():
        secret_token = secret_manager.get_secret("token_secret")
    else:
        secret_token = settings.TOKEN_SECRET
    return secret_token


def verify_internal_bot(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    # circular import
    from wacruit.src.apps.member.config import discord_config  # noqa

    if credentials.credentials != discord_config.bot_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bot token",
        )
    return credentials.credentials


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
