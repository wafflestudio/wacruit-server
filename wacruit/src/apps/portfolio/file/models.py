from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP
from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP_ON_UPDATE
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255


class PortfolioFile(DeclarativeBase):
    __tablename__ = "portfolio_file"

    id: Mapped[intpk]
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    generation: Mapped[int | None] = mapped_column(
        ForeignKey("recruiting.id", ondelete="SET NULL")
    )
    file_name: Mapped[str255] = mapped_column(nullable=False)
    is_uploaded: Mapped[bool] = mapped_column(nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP_ON_UPDATE,
    )
