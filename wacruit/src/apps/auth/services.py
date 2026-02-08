from datetime import datetime
from datetime import timedelta
from typing import Annotated

from authlib.jose import jwt
from authlib.jose import JWTClaims
from authlib.jose.errors import JoseError
from fastapi import Depends
from pydantic import EmailStr

from wacruit.src.apps.auth.exceptions import InvalidTokenException
from wacruit.src.apps.auth.exceptions import UserNotFoundException
from wacruit.src.apps.auth.repositories import AuthRepository
from wacruit.src.apps.common.security import get_token_secret
from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.user.models import User


class AuthService:
    def __init__(
        self,
        auth_repository: Annotated[AuthRepository, Depends()],
        token_secret: Annotated[str, Depends(get_token_secret)],
    ) -> None:
        self.auth_repository = auth_repository
        self.token_secret = token_secret

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.auth_repository.get_user_by_id(user_id)

    def login(self, email: EmailStr, password: str) -> tuple[str, str]:
        user = self.auth_repository.get_user_by_email(email)

        if user is None:
            raise UserNotFoundException()
        if user.password is None:
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
            claims = jwt.decode(token, key=self.token_secret)
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

        return jwt.encode(header, payload, key=self.token_secret).decode("utf-8")

    def check_available_email(self, email: EmailStr) -> bool:
        user = self.auth_repository.get_user_by_email(email)
        if user:
            return False
        return True
