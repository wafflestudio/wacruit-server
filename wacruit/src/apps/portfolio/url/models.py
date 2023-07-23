from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.user.models import User


class PortfolioUrl(DeclarativeBase):
    __tablename__ = "portfolio_url"

    id: Mapped[intpk]
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    url: Mapped[str] = mapped_column(str255, nullable=False)

    # user: Mapped["User"] = relationship(back_populates="portfolio_upload")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),  # pylint: disable=not-callable
        server_default=func.now(),  # pylint: disable=not-callable
    )
