from typing import Iterable

import pytest
import sqlalchemy
from sqlalchemy import orm

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.config import db_config


@pytest.fixture(scope="session")
def db_engine() -> Iterable[sqlalchemy.Engine]:
    url = db_config.url
    engine = sqlalchemy.create_engine(url)
    DeclarativeBase.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
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
