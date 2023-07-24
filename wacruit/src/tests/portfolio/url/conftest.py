import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.portfolio.url.repositories import PortfolioUrlRepository
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.services import UserService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def user1() -> User:
    return User(
        sso_id="abcdef111",
        first_name="Test1",
        last_name="User1",
        phone_number="010-1111-1111",
        email="example1@email.com",
        is_admin=False,
    )


@pytest.fixture
def user2() -> User:
    return User(
        sso_id="abcdef222",
        first_name="Test2",
        last_name="User2",
        phone_number="020-2222-2222",
        email="example2@email.com",
        is_admin=False,
    )


@pytest.fixture
def user_repository(db_session: Session):
    return UserRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def user_service(user_repository: UserRepository):
    return UserService(user_repository=user_repository)


@pytest.fixture
def created_user1(user_repository: UserRepository, user1: User) -> User:
    return user_repository.create_user(user1)


@pytest.fixture
def created_user2(user_repository: UserRepository, user2: User) -> User:
    return user_repository.create_user(user2)


@pytest.fixture
def portfolio_url_repository(db_session: Session):
    return PortfolioUrlRepository(
        session=db_session, transaction=Transaction(db_session)
    )


@pytest.fixture
def portfolio_url_service(portfolio_url_repository: PortfolioUrlRepository):
    return PortfolioUrlService(portfolio_url_repository=portfolio_url_repository)
