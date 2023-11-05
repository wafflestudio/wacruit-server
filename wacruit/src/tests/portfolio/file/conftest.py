import boto3
import moto
import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.portfolio.file.repositories import PortfolioFileRepository
from wacruit.src.apps.portfolio.file.services_v2 import PortfolioFileService
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
def portfolio_file_repository(db_session: Session):
    return PortfolioFileRepository(
        session=db_session, transaction=Transaction(db_session)
    )


@pytest.fixture
@moto.mock_s3
def portfolio_file_service(portfolio_file_repository: PortfolioFileRepository):
    s3_client = boto3.client("s3", region_name="ap-northeast-2")
    s3_client.create_bucket(
        Bucket="wacruit-portfolio-dev",
        CreateBucketConfiguration={"LocationConstraint": "ap-northeast-2"},
    )
    return PortfolioFileService(portfolio_file_repository=portfolio_file_repository)
