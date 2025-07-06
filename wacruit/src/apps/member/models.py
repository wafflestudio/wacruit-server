from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str50
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.project.models import Project
    from wacruit.src.apps.project.models import ProjectMember
    from wacruit.src.apps.review.models import Review


class Member(DeclarativeBase):
    __tablename__ = "member"

    id: Mapped[intpk]
    first_name: Mapped[str30]
    last_name: Mapped[str30]
    department: Mapped[str50 | None]
    college: Mapped[str50 | None]
    phone_number: Mapped[str30 | None]
    github_id: Mapped[str30 | None]
    generation: Mapped[str30]
    is_active: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(server_default=CURRENT_TIMESTAMP)

    leading_projects: Mapped[list["Project"]] = relationship(back_populates="leader")
    projects: Mapped[list["ProjectMember"]] = relationship(back_populates="member")
    review: Mapped["Review"] = relationship(back_populates="member")
