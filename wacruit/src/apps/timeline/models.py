from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.common.enums import TimelineGroupType
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30


class Timeline(DeclarativeBase):
    __tablename__ = "timeline"

    id: Mapped[intpk]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("timeline_category.id"), nullable=False
    )
    group: Mapped[TimelineGroupType]
    title: Mapped[str30]
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    category: Mapped["TimelineCategory"] = relationship("TimelineCategory")


class TimelineCategory(DeclarativeBase):
    __tablename__ = "timeline_category"

    id: Mapped[intpk]
    title: Mapped[str30]
