from datetime import date

from sqlalchemy import Date
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30


class Sponsor(DeclarativeBase):
    __tablename__ = "sponsor"

    id: Mapped[intpk]
    name: Mapped[str30]
    amount: Mapped[int]
    email: Mapped[str30 | None]
    phone_number: Mapped[str30 | None]
    sponsored_date: Mapped[date] = mapped_column(Date)
