from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.models.base import DeclarativeBase
from wacruit.src.database.models.base import intpk
from wacruit.src.database.models.base import str30

if TYPE_CHECKING:
    from wacruit.src.database.models.user import User


team_user_association = Table(
    "team_user_association",
    DeclarativeBase.metadata,
    Column(
        "team_id",
        Integer,
        ForeignKey("team.id"),
        primary_key=True,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("user.id"),
        primary_key=True,
    ),
)


class Team(DeclarativeBase):
    __tablename__ = "team"

    id: Mapped[intpk]
    name: Mapped[str30]
    introduction: Mapped[str] = mapped_column(String(1000), nullable=True)
    users: Mapped[list["User"]] = relationship(
        secondary=team_user_association,
        back_populates="teams",
    )
