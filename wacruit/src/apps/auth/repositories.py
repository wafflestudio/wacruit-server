from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wacruit.src.apps.auth.models import BlockedToken
from wacruit.src.apps.user.models import User
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class AuthRepository:
    def __init__(
        self,
        session: Annotated[Session, Depends(get_db_session)],
        transaction: Annotated[Transaction, Depends()],
    ) -> None:
        self.session = session
        self.transaction = transaction

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.query(User).where(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).where(User.id == user_id).first()

    def is_blocked_token(self, token: str) -> bool:
        result = (
            self.session.query(BlockedToken).where(BlockedToken.token == token).first()
        )
        if result:
            return True
        return False

    def block_token(self, token: str) -> bool:
        to_block = BlockedToken(token=token)
        with self.transaction:
            self.session.add(to_block)
        return True
