from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str50

if TYPE_CHECKING:
    from wacruit.src.apps.problem.models import CodeSubmission


class User(DeclarativeBase):
    __tablename__ = "user"

    id: Mapped[intpk]
    sso_id: Mapped[str50 | None]

    first_name: Mapped[str30]
    last_name: Mapped[str30]

    phone_number: Mapped[str30]
    email: Mapped[str50] = mapped_column(unique=True)

    department: Mapped[str50 | None]
    college: Mapped[str50 | None]
    university: Mapped[str50 | None]

    code_submissions: Mapped[list["CodeSubmission"]] = relationship(
        back_populates="user", cascade="all, delete"
    )

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
