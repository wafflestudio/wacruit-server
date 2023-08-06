from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP
from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP_ON_UPDATE
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk


class Announcement(DeclarativeBase):
    __tablename__ = "announcement"
    id: Mapped[intpk]
    title: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str | None] = mapped_column(Text)
    pinned: Mapped[bool] = mapped_column(server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP_ON_UPDATE,
    )
