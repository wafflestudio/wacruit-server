from datetime import datetime, timedelta

import boto3
import moto
import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.portfolio.file.aws.config import storage_config
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.file.repositories import PortfolioFileRepository
from wacruit.src.apps.portfolio.file.services_v2 import PortfolioFileService
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.services import UserService
from wacruit.src.database.connection import Transaction
from wacruit.src.utils.singleton import SingletonMeta


@pytest.fixture
def user1(db_session: Session) -> User:
    user1 = User(
        sso_id="abcdef111",
        first_name="Test1",
        last_name="User1",
        phone_number="010-1111-1111",
        email="example1@email.com",
        is_admin=False,
        password=PasswordService.hash_password("password123"),
    )
    db_session.add(user1)
    db_session.commit()
    return user1


@pytest.fixture
def recruiting1(db_session: Session) -> Recruiting:
    recruiting = Recruiting(
        name="2023-루키-리크루팅",
        is_active=True,
        from_date=datetime.today() - timedelta(days=7),
        to_date=datetime.today() + timedelta(days=7),
        description="2023 루키 리크루팅입니다.",
        short_description="2023 루키 리크루팅",
    )
    db_session.add(recruiting)
    db_session.commit()
    return recruiting


@pytest.fixture
def recruiting2(db_session: Session) -> Recruiting:
    recruiting = Recruiting(
        name="2024-루키-리크루팅",
        is_active=True,
        from_date=datetime.today() - timedelta(days=7),
        to_date=datetime.today() + timedelta(days=7),
        description="2024 루키 리크루팅입니다.",
        short_description="2024 루키 리크루팅",
    )
    db_session.add(recruiting)
    db_session.commit()
    return recruiting


@pytest.fixture
def user_repository(db_session: Session):
    return UserRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def user_service(user_repository: UserRepository):
    return UserService(user_repository=user_repository)


@pytest.fixture
def recruiting_repository(db_session: Session) -> RecruitingRepository:
    return RecruitingRepository(db_session, Transaction(db_session))


@pytest.fixture
def portfolio_file_repository(db_session: Session):
    return PortfolioFileRepository(
        session=db_session, transaction=Transaction(db_session)
    )


@pytest.fixture
def portfolio_file_service(
    portfolio_file_repository: PortfolioFileRepository,
    recruiting_repository: RecruitingRepository,
):
    with moto.mock_s3():
        storage_config.bucket_name = "wacruit-portfolio-test"
        storage_config.region = "ap-northeast-2"
        storage_config.endpoint_url = None
        storage_config.access_key_id = "testing"
        storage_config.secret_access_key = "testing"
        storage_config.addressing_style = "path"
        SingletonMeta._instances.pop(S3Client, None)

        s3_client = boto3.client(
            "s3",
            region_name=storage_config.region,
            aws_access_key_id=storage_config.access_key_id,
            aws_secret_access_key=storage_config.secret_access_key,
        )
        s3_client.create_bucket(
            Bucket=storage_config.bucket_name,
            CreateBucketConfiguration={"LocationConstraint": storage_config.region},
        )
        yield PortfolioFileService(
            portfolio_file_repository=portfolio_file_repository,
            recruiting_repository=recruiting_repository,
        )
        SingletonMeta._instances.pop(S3Client, None)
