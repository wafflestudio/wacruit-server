from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30

if TYPE_CHECKING:
    from wacruit.src.apps.problem.models import Problem
    from wacruit.src.apps.resume.models import ResumeQuestion
    from wacruit.src.apps.resume.models import ResumeSubmission


class Recruiting(DeclarativeBase):
    __tablename__ = "recruiting"

    id: Mapped[intpk]
    name: Mapped[str30]
    is_active: Mapped[bool]
    from_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    to_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    description: Mapped[str] = mapped_column(Text)

    resume_submissions: Mapped[list["ResumeSubmission"]] = relationship(
        back_populates="recruiting"
    )
    resume_questions: Mapped[list["ResumeQuestion"]] = relationship(
        back_populates="recruiting"
    )
    problems: Mapped[list["Problem"]] = relationship(back_populates="recruiting")

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
            problems.append({"num": problem.num, "status": status})
        return problems

    def __str__(self):
        return (
            f"<Recruiting id={self.id}, "
            f"name={self.name}, "
            f"is_active={self.is_active}, "
            f"from={self.from_date}, "
            f"to={self.to_date}>"
        )
