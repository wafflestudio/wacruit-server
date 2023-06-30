from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from wacruit.src.database import base as base_model
from wacruit.src.database.base import intpk
from wacruit.src.database.base import mapped_column
from wacruit.src.database.base import str30

if TYPE_CHECKING:
    from wacruit.src.database.models.user import User


class SNSAccount(base_model.DeclarativeBase):
    __tablename__ = "sns_account"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
    )
    user: Mapped["User"] = relationship(back_populates="sns_accounts")
    name: Mapped[str30]
    url: Mapped[str] = mapped_column(String(200))
