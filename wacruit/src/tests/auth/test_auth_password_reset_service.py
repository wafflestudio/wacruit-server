from datetime import datetime
from datetime import timedelta

from pydantic import EmailStr
import pytest

from wacruit.src.apps.auth.exceptions import ExpiredPasswordResetCodeException
from wacruit.src.apps.auth.exceptions import InvalidPasswordResetCodeException
from wacruit.src.apps.auth.exceptions import PasswordResetCodeNotVerifiedException
from wacruit.src.apps.auth.models import PasswordResetVerification
from wacruit.src.apps.auth.services import AuthService
from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.user.models import User
from wacruit.src.tests.auth.conftest import FakeAuthRepository
from wacruit.src.tests.auth.conftest import FakeEmailService


def test_send_password_reset_email_creates_verification(
    auth_service: AuthService,
    auth_repository: FakeAuthRepository,
    fake_email_service: FakeEmailService,
    user: User,
):
    auth_service._generate_password_reset_code = lambda: "123456"  # type: ignore

    auth_service.send_password_reset_email(EmailStr(user.email))

    verification = auth_repository.get_latest_password_reset_verification(
        EmailStr(user.email)
    )
    assert verification is not None
    assert PasswordService.verify_password("123456", verification.code_hash)
    assert fake_email_service.sent_password_reset_codes == [(user.email, "123456")]


def test_send_password_reset_email_ignores_unknown_email(
    auth_service: AuthService,
    auth_repository: FakeAuthRepository,
    fake_email_service: FakeEmailService,
):
    email = EmailStr("unknown@email.com")

    auth_service.send_password_reset_email(email)

    assert auth_repository.get_latest_password_reset_verification(email) is None
    assert fake_email_service.sent_password_reset_codes == []


def test_verify_password_reset_code(
    auth_service: AuthService,
    auth_repository: FakeAuthRepository,
    user: User,
):
    auth_service._generate_password_reset_code = lambda: "123456"  # type: ignore
    auth_service.send_password_reset_email(EmailStr(user.email))

    auth_service.verify_password_reset_code(EmailStr(user.email), "123456")

    verification = auth_repository.get_latest_password_reset_verification(
        EmailStr(user.email)
    )
    assert verification is not None
    assert verification.verified_at is not None


def test_verify_password_reset_code_rejects_wrong_code(
    auth_service: AuthService,
    auth_repository: FakeAuthRepository,
    user: User,
):
    auth_service._generate_password_reset_code = lambda: "123456"  # type: ignore
    auth_service.send_password_reset_email(EmailStr(user.email))

    with pytest.raises(InvalidPasswordResetCodeException):
        auth_service.verify_password_reset_code(EmailStr(user.email), "000000")

    verification = auth_repository.get_latest_password_reset_verification(
        EmailStr(user.email)
    )
    assert verification is not None
    assert verification.attempt_count == 1


def test_verify_password_reset_code_rejects_expired_code(
    auth_service: AuthService,
    auth_repository: FakeAuthRepository,
    user: User,
):
    verification = PasswordResetVerification(
        email=user.email,
        code_hash=PasswordService.hash_password("123456"),
        expires_at=datetime.now() - timedelta(minutes=1),
    )
    auth_repository.create_password_reset_verification(verification)

    with pytest.raises(ExpiredPasswordResetCodeException):
        auth_service.verify_password_reset_code(EmailStr(user.email), "123456")


def test_reset_password_requires_verified_code(
    auth_service: AuthService,
    user: User,
):
    auth_service._generate_password_reset_code = lambda: "123456"  # type: ignore
    auth_service.send_password_reset_email(EmailStr(user.email))

    with pytest.raises(PasswordResetCodeNotVerifiedException):
        auth_service.reset_password(EmailStr(user.email), "123456", "new-password")


def test_reset_password_updates_password(
    auth_service: AuthService,
    auth_repository: FakeAuthRepository,
    user: User,
):
    auth_service._generate_password_reset_code = lambda: "123456"  # type: ignore
    auth_service.send_password_reset_email(EmailStr(user.email))
    auth_service.verify_password_reset_code(EmailStr(user.email), "123456")

    auth_service.reset_password(EmailStr(user.email), "123456", "new-password")

    updated_user = auth_repository.get_user_by_email(EmailStr(user.email))
    verification = auth_repository.get_latest_password_reset_verification(
        EmailStr(user.email)
    )
    assert updated_user is not None
    assert updated_user.password is not None
    assert PasswordService.verify_password("new-password", updated_user.password)
    assert verification is not None
    assert verification.used_at is not None
