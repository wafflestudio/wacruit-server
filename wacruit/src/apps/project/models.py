from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str50
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.member.models import Member

project_member_association = Table(
    "project_member_association",
    DeclarativeBase.metadata,
    Column("member_id", ForeignKey("member.id")),
    Column("project_id", ForeignKey("project.id")),
)


class Project(DeclarativeBase):
    __tablename__ = "project"

    id: Mapped[intpk]
    name: Mapped[str30]
    summary: Mapped[str50 | None]
    introduction: Mapped[str255 | None]
    thumbnail_url: Mapped[str255 | None]
    leader_id: Mapped[int] = mapped_column(ForeignKey("member.id"))
    is_service: Mapped[bool]

    leader: Mapped["Member"] = relationship(back_populates="leading_projects")
    members: Mapped[list["Member"]] = relationship(
        secondary=project_member_association, back_populates="projects"
    )
    urls: Mapped[list["ProjectURL"]] = relationship(back_populates="source_project")


class ProjectURL(DeclarativeBase):
    __tablename__ = "project_url"

    id: Mapped[intpk]
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    url: Mapped[str255]

    source_project: Mapped["Project"] = relationship(back_populates="urls")
