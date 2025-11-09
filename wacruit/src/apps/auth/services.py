from datetime import datetime
from datetime import timedelta
from typing import Annotated

from authlib.jose import jwt
from authlib.jose import JWTClaims
from authlib.jose.errors import JoseError
from fastapi import Depends

from wacruit.src.apps.auth.exceptions import InvalidTokenException
from wacruit.src.apps.auth.exceptions import UserNotFoundException
from wacruit.src.apps.auth.repositories import AuthRepository
from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.user.models import User
from wacruit.src.secrets import AWSSecretManager
from wacruit.src.settings import settings


class AuthService:
    def __init__(
        self,
        auth_repository: Annotated[AuthRepository, Depends()],
    ) -> None:
        self.secret_manager = AWSSecretManager()
        self.auth_repository = auth_repository

        if self.secret_manager.is_available():
            self.secret_token = self.secret_manager.get_secret("token_secret")
        else:
            self.secret_token = settings.TOKEN_SECRET

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.auth_repository.get_user_by_id(user_id)

    def login(self, username: str, password: str) -> tuple[str, str]:
        user = self.auth_repository.get_user_by_username(username)

        if user is None:
            raise UserNotFoundException()

        if PasswordService.verify_password(password, user.password):
            access_token = self.issue_token(user.id, 24, "access")
            refresh_token = self.issue_token(user.id, 24 * 7, "refresh")
            return (access_token, refresh_token)
        raise UserNotFoundException()

    def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        decoded_token = self.decode_token(refresh_token)
        if decoded_token["token_type"] != "refresh":
            raise UserNotFoundException()

        user_id = decoded_token["sub"]
        user = self.auth_repository.get_user_by_id(user_id)

        if self.auth_repository.is_blocked_token(refresh_token):
            raise UserNotFoundException()
        if user is None:
            raise UserNotFoundException()

        self.block_token(refresh_token)
        access_token = self.issue_token(user.id, 24, "access")
        new_refresh_token = self.issue_token(user.id, 24 * 7, "refresh")
        return (access_token, new_refresh_token)

    def block_token(self, token: str) -> None:
        if self.auth_repository.is_blocked_token(token):
            raise InvalidTokenException()

        self.auth_repository.block_token(token)

    def decode_token(self, token: str) -> JWTClaims:
        try:
            claims = jwt.decode(token, key=self.secret_token)
            claims.validate()
            return claims
        except JoseError as e:
            raise InvalidTokenException() from e

    def issue_token(self, user_id: int, expiration_hour: int, token_type: str) -> str:
        header = {"alg": "HS256"}
        payload = {
            "sub": user_id,
            "exp": int((datetime.now() + timedelta(hours=expiration_hour)).timestamp()),
            "token_type": token_type,
        }

        return jwt.encode(header, payload, key=self.secret_token).decode("utf-8")
