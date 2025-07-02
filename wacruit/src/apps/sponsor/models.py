from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30


class Sponsor(DeclarativeBase):
    __tablename__ = "sponsor"

    id: Mapped[intpk]
    name: Mapped[str30]
    amount: Mapped[str30]
    email: Mapped[str30 | None]
    phone_number: Mapped[str30 | None]
    sponsored_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
