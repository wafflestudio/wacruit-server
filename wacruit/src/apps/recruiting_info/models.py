from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str50


class RecruitingInfo(DeclarativeBase):
    __tablename__ = "recruiting_info"

    id: Mapped[intpk]
    info_num: Mapped[int]
    title: Mapped[str50]
    date_info: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
