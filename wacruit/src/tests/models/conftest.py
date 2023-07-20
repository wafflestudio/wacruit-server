import pytest

from wacruit.src.apps.user.models import User


@pytest.fixture
def user() -> User:
    return User(
        sso_id="abcdef123",
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="test@test.com",
        is_admin=False,
    )
