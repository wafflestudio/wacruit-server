from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str50

if TYPE_CHECKING:
    from wacruit.src.apps.recruiting.models import Recruiting


class RecruitingInfo(DeclarativeBase):
    __tablename__ = "recruiting_info"

    id: Mapped[intpk]
    info_num: Mapped[int]
    title: Mapped[str50]
    date_info: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    recruiting_id: Mapped[int] = mapped_column(ForeignKey("recruiting.id"))

    recruting: Mapped["Recruiting"] = relationship(back_populates="recruiting_info")
