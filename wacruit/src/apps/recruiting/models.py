from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import text
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import RecruitingApplicationStatus
from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP
from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP_ON_UPDATE
from wacruit.src.apps.user.models import User
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.problem.models import Problem
    from wacruit.src.apps.resume.models import ResumeQuestion
    from wacruit.src.apps.resume.models import ResumeSubmission


class Recruiting(DeclarativeBase):
    __tablename__ = "recruiting"

    id: Mapped[intpk]
    name: Mapped[str30]
    type: Mapped[RecruitingType] = mapped_column(server_default=text("'ROOKIE'"))
    is_active: Mapped[bool]
    from_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    to_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    short_description: Mapped[str255]
    description: Mapped[str] = mapped_column(Text)

    resume_submissions: Mapped[list["ResumeSubmission"]] = relationship(
        back_populates="recruiting"
    )
    resume_questions: Mapped[list["ResumeQuestion"]] = relationship(
        back_populates="recruiting"
    )
    problems: Mapped[list["Problem"]] = relationship(back_populates="recruiting")
    applicants: Mapped[list["RecruitingApplication"]] = relationship(
        back_populates="recruiting"
    )

    @property
    def is_open(self):
        from_date = self.from_date or datetime.min
        to_date = self.to_date or datetime.max
        return self.is_active and (
            from_date < datetime.utcnow() + timedelta(hours=9) < to_date
        )

    @property
    def problem_status(self):
        problems = []
        for problem in self.problems:
            status = CodeSubmissionStatus.NOT_SUBMITTED
            if problem.submissions:
                status = problem.submissions[0].status.value
                for submission in problem.submissions:
                    if submission.status == CodeSubmissionStatus.SOLVED:
                        status = CodeSubmissionStatus.SOLVED.value
                        break
            problems.append({"id": problem.id, "num": problem.num, "status": status})
        return problems

    @property
    def applied(self):
        print(self.applicants)
        return len(self.applicants) > 0

    def __str__(self):
        return (
            f"<Recruiting id={self.id}, "
            f"name={self.name}, "
            f"type={self.type}, "
            f"is_active={self.is_active}, "
            f"from={self.from_date}, "
            f"to={self.to_date}>"
        )


class RecruitingApplication(DeclarativeBase):
    __tablename__ = "recruiting_application"
    __table_args__ = (
        UniqueConstraint("user_id", "recruiting_id", name="ak_user_recruiting"),
    )

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    recruiting_id: Mapped[int] = mapped_column(
        ForeignKey("recruiting.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[RecruitingApplicationStatus] = mapped_column(
        server_default=text("'IN_PROGRESS'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP_ON_UPDATE,
    )

    recruiting: Mapped[Recruiting] = relationship("Recruiting")
    user: Mapped["User"] = relationship("User")

    def __str__(self):
        return (
            f"<RecruitingApplication id={self.id}, "
            f"user_id={self.user_id}, "
            f"recruiting_id={self.recruiting_id}, "
            f"status={self.status}>"
        )
