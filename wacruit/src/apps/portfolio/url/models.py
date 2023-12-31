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


class PortfolioUrl(DeclarativeBase):
    __tablename__ = "portfolio_url"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    recruiting_id: Mapped[int] = mapped_column(
        ForeignKey("recruiting.id", ondelete="CASCADE"), default=None
    )
    url: Mapped[str255] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP_ON_UPDATE,
    )
