from datetime import datetime

from sqlalchemy.orm import Mapped

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk


class History(DeclarativeBase):
    __tablename__ = "histroy"

    id: Mapped[intpk]
    total_projects: Mapped[int]
    total_users: Mapped[int]
    total_members: Mapped[int]
