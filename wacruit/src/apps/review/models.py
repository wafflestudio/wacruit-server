from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str255
from wacruit.src.database.base import str1500

if TYPE_CHECKING:
    from wacruit.src.apps.member.models import Member


class Review(DeclarativeBase):
    __tablename__ = "review"

    id: Mapped[intpk]
    title: Mapped[str30]
    content: Mapped[str1500]
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"))

    member: Mapped["Member"] = relationship(back_populates="review")
