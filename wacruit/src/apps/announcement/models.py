from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import text

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk


class Announcement(DeclarativeBase):
    __tablename__ = "announcement"
    id: Mapped[intpk]
    title: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str | None] = mapped_column(String(10000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),  # pylint: disable=not-callable
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=text("CURRENT_TIMESTAMP"),  # pylint: disable=not-callable
        server_default=text("CURRENT_TIMESTAMP"),  # pylint: disable=not-callable
    )
