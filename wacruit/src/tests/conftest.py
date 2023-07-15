from typing import Iterable

import pytest
import sqlalchemy
from sqlalchemy import orm

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.config import db_config
from wacruit.src.settings import settings


@pytest.fixture(autouse=True, scope="session")
def set_test_env():
    settings.env = "test"


@pytest.fixture(scope="session")
def db_engine(set_test_env) -> Iterable[sqlalchemy.Engine]:
    url = db_config.url
    engine = sqlalchemy.create_engine(url)
    DeclarativeBase.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        DeclarativeBase.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine: sqlalchemy.Engine) -> Iterable[orm.Session]:
    connection = db_engine.connect()
    transaction = connection.begin_nested()

    session_maker = orm.sessionmaker(
        connection,
        expire_on_commit=True,
    )

    session = session_maker()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
