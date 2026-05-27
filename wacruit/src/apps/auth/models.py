from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255


class BlockedToken(DeclarativeBase):
    __tablename__ = "blocked_token"

    id: Mapped[intpk]
    token: Mapped[str255]


class PasswordResetVerification(DeclarativeBase):
    __tablename__ = "password_reset_verification"

    id: Mapped[intpk]
    email: Mapped[str255] = mapped_column(index=True)
    code_hash: Mapped[str255]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempt_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP,
    )
