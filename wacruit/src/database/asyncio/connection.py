from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import close_all_sessions

from wacruit.src.database.asyncio.config import db_config
from wacruit.src.settings import settings
from wacruit.src.utils.singleton import SingletonMeta


class AsyncDBSessionFactory(metaclass=SingletonMeta):
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(
            db_config.url,
            echo=settings.is_local,
            pool_recycle=28000,
            pool_pre_ping=True,
        )
        self.session_maker = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    def get_engine(self) -> AsyncEngine:
        return self.engine

    def make_session(self) -> AsyncSession:
        session = self.session_maker()
        return session

    async def teardown(self):
        close_all_sessions()
        await self.engine.dispose()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    session = AsyncDBSessionFactory().make_session()

    try:
        yield session
    finally:
        await session.commit()
        await session.close()


class AsyncTransaction:
    """
    A context manager class for flushing changes to the database without committing
    the transaction. This class can be used to check for integrity errors before
    committing the transaction. The transaction is committed when the scope of each
    request is finished. See `get_db_session` for more details.
    """

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def __aenter__(self):
        self.session.begin_nested()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            # rollback and let the exception propagate
            await self.session.rollback()
            return False

        await self.session.flush()
        return True
