from sqlalchemy import CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str50
from wacruit.src.database.base import str255


class PreRegistration(DeclarativeBase):
    __tablename__ = "pre_registration"
    __table_args__ = (
        UniqueConstraint("active_key", name="uk_pre_registration_active"),
        CheckConstraint(
            "active_key IS NULL OR active_key = 1",
            name="ck_pre_registration_active_key",
        ),
    )

    id: Mapped[intpk]
    url: Mapped[str255]
    generation: Mapped[str30]
    is_active: Mapped[bool]
    active_key: Mapped[int | None] = mapped_column(default=None, nullable=True)

    users: Mapped[list["PreRegistrationUser"]] = relationship(
        back_populates="pre_registration"
    )

    @validates("is_active")
    def validate_is_active(self, _key: str, is_active: bool) -> bool:
        self.active_key = 1 if is_active else None
        return is_active


class PreRegistrationUser(DeclarativeBase):
    __tablename__ = "pre_registration_user"
    __table_args__ = (
        UniqueConstraint(
            "pre_registration_id",
            "email",
            name="uk_pre_registration_user_email",
        ),
    )

    id: Mapped[intpk]
    pre_registration_id: Mapped[int] = mapped_column(
        ForeignKey("pre_registration.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str50]
    email: Mapped[str255]
    phone_number: Mapped[str30]
    university: Mapped[str50 | None]
    college: Mapped[str50 | None]
    department: Mapped[str50 | None]

    pre_registration: Mapped["PreRegistration"] = relationship(back_populates="users")
