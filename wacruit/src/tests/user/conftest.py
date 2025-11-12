import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.common.security import PasswordService
import wacruit.src.apps.problem.models  # nopycln: import
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.services import UserService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def user() -> User:
    return User(
        sso_id="abcdef123",
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="example@email.com",
        is_admin=False,
        username="name",
        password=PasswordService.hash_password("password123"),
    )


@pytest.fixture
def user_repository(db_session: Session):
    return UserRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def user_service(user_repository: UserRepository):
    return UserService(user_repository=user_repository)


@pytest.fixture
def created_user(user_repository: UserRepository, user: User) -> User:
    return user_repository.create_user(user)
