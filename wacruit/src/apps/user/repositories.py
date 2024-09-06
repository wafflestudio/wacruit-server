from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wacruit.src.apps.user.models import User
from wacruit.src.database.asyncio.connection import AsyncTransaction
from wacruit.src.database.asyncio.connection import get_db_session


class UserRepository:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        transaction: Annotated[AsyncTransaction, Depends()],
    ):
        self.session = session
        self.transaction = transaction

    async def check_signup_by_sso_id(self, sso_id: str) -> bool:
        result = (
            await self.session.execute(select(User).filter(User.sso_id == sso_id))
        ).one_or_none()
        return result is not None

    async def get_users(self) -> Sequence[User]:
        return (await self.session.execute(select(User))).scalars().all()

    async def get_user_by_id(self, user_id: int) -> User | None:
        return (
            await self.session.execute(select(User).filter(User.id == user_id))
        ).scalar()

    async def get_user_by_sso_id(self, sso_id: str) -> User | None:
        return (
            await self.session.execute(select(User).filter(User.sso_id == sso_id))
        ).scalar()

    async def create_user(self, user: User) -> User:
        async with self.transaction:
            self.session.add(user)
            await self.session.flush()
        return user

    async def create_users(self, users: list[User]) -> None:
        async with self.transaction:
            self.session.add_all(users)

    async def update_user(self, user: User) -> User | None:
        if await self.get_user_by_id(user.id) is None:
            return None

        async with self.transaction:
            await self.session.merge(user)

        return user
