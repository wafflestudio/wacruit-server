from datetime import datetime

from pydantic import EmailStr
import pytest

from wacruit.src.apps.auth.models import PasswordResetVerification
from wacruit.src.apps.auth.services import AuthService
from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.user.models import User


class FakeAuthRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.verifications: list[PasswordResetVerification] = []

    def get_user_by_email(self, email: EmailStr) -> User | None:
        return self.users.get(str(email))

    def get_user_by_id(self, user_id: int) -> User | None:
        return next((user for user in self.users.values() if user.id == user_id), None)

    def update_user(self, user: User) -> User:
        self.users[user.email] = user
        return user

    def create_password_reset_verification(
        self, verification: PasswordResetVerification
    ) -> PasswordResetVerification:
        verification.id = len(self.verifications) + 1
        verification.created_at = datetime.now()
        verification.attempt_count = verification.attempt_count or 0
        self.verifications.append(verification)
        return verification

    def get_latest_password_reset_verification(
        self, email: EmailStr
    ) -> PasswordResetVerification | None:
        verifications = [
            verification
            for verification in self.verifications
            if verification.email == str(email)
        ]
        if not verifications:
            return None
        return max(
            verifications,
            key=lambda verification: (verification.created_at, verification.id),
        )

    def update_password_reset_verification(
        self, verification: PasswordResetVerification
    ) -> PasswordResetVerification:
        return verification

    def expire_unused_password_reset_verifications(
        self, email: EmailStr, expires_at: datetime
    ) -> None:
        for verification in self.verifications:
            if verification.email == str(email) and verification.used_at is None:
                verification.expires_at = expires_at

    def is_blocked_token(self, token: str) -> bool:
        return False

    def block_token(self, token: str) -> bool:
        return True


class FakeEmailService:
    def __init__(self) -> None:
        self.sent_password_reset_codes: list[tuple[str, str]] = []

    def send_password_reset_code(self, to_email: str, code: str) -> None:
        self.sent_password_reset_codes.append((to_email, code))


@pytest.fixture
def auth_repository() -> FakeAuthRepository:
    return FakeAuthRepository()


@pytest.fixture
def fake_email_service() -> FakeEmailService:
    return FakeEmailService()


@pytest.fixture
def auth_service(
    auth_repository: FakeAuthRepository, fake_email_service: FakeEmailService
) -> AuthService:
    return AuthService(
        auth_repository=auth_repository,  # type: ignore[arg-type]
        token_secret="test-secret",
        email_service=fake_email_service,  # type: ignore[arg-type]
    )


@pytest.fixture
def user(auth_repository: FakeAuthRepository) -> User:
    user = User(
        id=1,
        sso_id="abcdef123",
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="example@email.com",
        is_admin=False,
        password=PasswordService.hash_password("password123"),
    )
    auth_repository.users[user.email] = user
    return user
