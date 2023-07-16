from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str50
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.problem.models import CodeSubmission
    from wacruit.src.apps.resume.models import ResumeSubmission


class User(DeclarativeBase):
    __tablename__ = "user"

    id: Mapped[intpk]
    sso_id: Mapped[str50 | None]

    first_name: Mapped[str30]
    last_name: Mapped[str30]

    phone_number: Mapped[str30]
    email: Mapped[str255] = mapped_column(unique=True)

    department: Mapped[str50 | None]
    college: Mapped[str50 | None]
    university: Mapped[str50 | None]

    github_email: Mapped[str255 | None]
    slack_email: Mapped[str255 | None]
    notion_email: Mapped[str255 | None]

    code_submissions: Mapped[list["CodeSubmission"]] = relationship(
        back_populates="user"
    )

    resume_submissions: Mapped[list["ResumeSubmission"]] = relationship(
        back_populates="user"
    )

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
