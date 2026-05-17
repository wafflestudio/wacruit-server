from datetime import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session

from wacruit.src.apps.auth.models import BlockedToken
from wacruit.src.apps.auth.models import PasswordResetVerification
from wacruit.src.apps.user.models import User
from wacruit.src.database.connection import Transaction
from wacruit.src.database.connection import get_db_session


class AuthRepository:
    def __init__(
        self,
        session: Annotated[Session, Depends(get_db_session)],
        transaction: Annotated[Transaction, Depends()],
    ) -> None:
        self.session = session
        self.transaction = transaction

    def get_user_by_email(self, email: EmailStr) -> User | None:
        return self.session.query(User).where(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).where(User.id == user_id).first()

    def update_user(self, user: User) -> User:
        with self.transaction:
            self.session.merge(user)
        return user

    def create_password_reset_verification(
        self, verification: PasswordResetVerification
    ) -> PasswordResetVerification:
        with self.transaction:
            self.session.add(verification)
        return verification

    def replace_active_password_reset_for_email(
        self,
        email: EmailStr,
        verification: PasswordResetVerification,
        expires_at: datetime,
    ) -> PasswordResetVerification:
        with self.transaction:
            (
                self.session.query(PasswordResetVerification)
                .where(
                    PasswordResetVerification.email == email,
                    PasswordResetVerification.used_at.is_(None),
                )
                .update(
                    {PasswordResetVerification.expires_at: expires_at},
                    synchronize_session="fetch",
                )
            )
            self.session.add(verification)
        return verification

    def get_latest_password_reset_verification(
        self, email: EmailStr
    ) -> PasswordResetVerification | None:
        return (
            self.session.query(PasswordResetVerification)
            .where(PasswordResetVerification.email == email)
            .order_by(
                PasswordResetVerification.created_at.desc(),
                PasswordResetVerification.id.desc(),
            )
            .first()
        )

    def update_password_reset_verification(
        self, verification: PasswordResetVerification
    ) -> PasswordResetVerification:
        with self.transaction:
            self.session.merge(verification)
        return verification

    def consume_password_reset_verification(
        self,
        verification_id: int,
        email: EmailStr,
        password_hash: str,
        used_at: datetime,
    ) -> bool:
        with self.transaction:
            verification = (
                self.session.query(PasswordResetVerification)
                .where(
                    PasswordResetVerification.id == verification_id,
                    PasswordResetVerification.email == email,
                )
                .with_for_update()
                .first()
            )
            if verification is None or verification.used_at is not None:
                return False

            user = (
                self.session.query(User)
                .where(User.email == email)
                .with_for_update()
                .first()
            )
            if user is None:
                return False

            user.password = password_hash
            verification.used_at = used_at
        return True

    def expire_unused_password_reset_verifications(
        self, email: EmailStr, expires_at: datetime
    ) -> None:
        verifications = (
            self.session.query(PasswordResetVerification)
            .where(
                PasswordResetVerification.email == email,
                PasswordResetVerification.used_at.is_(None),
            )
            .all()
        )
        with self.transaction:
            for verification in verifications:
                verification.expires_at = expires_at

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
