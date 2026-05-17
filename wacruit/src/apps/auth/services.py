from datetime import datetime
from datetime import timedelta
import secrets
from typing import Annotated

from authlib.jose import JWTClaims
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from fastapi import Depends
from pydantic import EmailStr

from wacruit.src.apps.auth.exceptions import ExpiredPasswordResetCodeException
from wacruit.src.apps.auth.exceptions import InvalidPasswordResetCodeException
from wacruit.src.apps.auth.exceptions import InvalidTokenException
from wacruit.src.apps.auth.exceptions import PasswordResetCodeNotVerifiedException
from wacruit.src.apps.auth.exceptions import UserNotFoundException
from wacruit.src.apps.auth.models import PasswordResetVerification
from wacruit.src.apps.auth.repositories import AuthRepository
from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.common.security import get_token_secret
from wacruit.src.apps.mail.services import EmailService
from wacruit.src.apps.user.models import User

PASSWORD_RESET_CODE_LENGTH = 6
PASSWORD_RESET_CODE_TTL_MINUTES = 10
PASSWORD_RESET_MAX_ATTEMPTS = 5


class AuthService:
    def __init__(
        self,
        auth_repository: Annotated[AuthRepository, Depends()],
        token_secret: Annotated[str, Depends(get_token_secret)],
        email_service: Annotated[EmailService, Depends()],
    ) -> None:
        self.auth_repository = auth_repository
        self.token_secret = token_secret
        self.email_service = email_service

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

    def send_password_reset_email(self, email: EmailStr) -> None:
        user = self.auth_repository.get_user_by_email(email)
        if user is None:
            return

        code = self._generate_password_reset_code()
        now = datetime.now()
        expires_at = now + timedelta(minutes=PASSWORD_RESET_CODE_TTL_MINUTES)

        self.email_service.send_password_reset_code(str(email), code)
        self.auth_repository.expire_unused_password_reset_verifications(email, now)
        self.auth_repository.create_password_reset_verification(
            PasswordResetVerification(
                email=email,
                code_hash=PasswordService.hash_password(code),
                expires_at=expires_at,
            )
        )

    def verify_password_reset_code(self, email: EmailStr, code: str) -> None:
        verification = self._get_valid_password_reset_verification(email, code)
        verification.verified_at = datetime.now()
        self.auth_repository.update_password_reset_verification(verification)

    def reset_password(self, email: EmailStr, code: str, new_password: str) -> None:
        verification = self._get_valid_password_reset_verification(email, code)
        if verification.verified_at is None:
            raise PasswordResetCodeNotVerifiedException()

        user = self.auth_repository.get_user_by_email(email)
        if user is None:
            raise UserNotFoundException()

        user.password = PasswordService.hash_password(new_password)
        verification.used_at = datetime.now()
        self.auth_repository.update_user(user)
        self.auth_repository.update_password_reset_verification(verification)

    def _generate_password_reset_code(self) -> str:
        max_value = 10**PASSWORD_RESET_CODE_LENGTH
        return str(secrets.randbelow(max_value)).zfill(PASSWORD_RESET_CODE_LENGTH)

    def _get_valid_password_reset_verification(
        self, email: EmailStr, code: str
    ) -> PasswordResetVerification:
        if not code.isdigit():
            raise InvalidPasswordResetCodeException()

        verification = self.auth_repository.get_latest_password_reset_verification(
            email
        )
        if verification is None or verification.used_at is not None:
            raise InvalidPasswordResetCodeException()

        now = datetime.now()
        if verification.expires_at < now:
            raise ExpiredPasswordResetCodeException()

        if verification.attempt_count >= PASSWORD_RESET_MAX_ATTEMPTS:
            raise InvalidPasswordResetCodeException()

        if not PasswordService.verify_password(code, verification.code_hash):
            verification.attempt_count += 1
            self.auth_repository.update_password_reset_verification(verification)
            raise InvalidPasswordResetCodeException()

        return verification
