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

from wacruit.src.apps.common.enums import ProjectType

if TYPE_CHECKING:
    from wacruit.src.apps.member.models import Member

class Project(DeclarativeBase):
    __tablename__ = "project"

    id: Mapped[intpk]
    name: Mapped[str30]
    summary: Mapped[str50 | None]
    introduction: Mapped[str255 | None]
    thumbnail_url: Mapped[str255 | None]
    leader_id: Mapped[int] = mapped_column(ForeignKey("member.id"))
    project_type: Mapped[ProjectType]
    is_active: Mapped[bool] = mapped_column(default=True)
    leader: Mapped["Member"] = relationship(back_populates="leading_projects")
    members: Mapped[list["ProjectMember"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    urls: Mapped[list["ProjectURL"] | None] = relationship(back_populates="source_project")
    image_urls: Mapped[list["ProjectImageURL"] | None] = relationship(
        back_populates="source_project"
    )


class ProjectURL(DeclarativeBase):
    __tablename__ = "project_url"

    id: Mapped[intpk]
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    title: Mapped[str50]
    url: Mapped[str255]

    source_project: Mapped["Project"] = relationship(back_populates="urls")


class ProjectImageURL(DeclarativeBase):
    __tablename__ = "project_image_url"

    id: Mapped[intpk]
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    url: Mapped[str255]

    source_project: Mapped["Project"] = relationship(back_populates="image_urls")

class ProjectMember(DeclarativeBase):
    __tablename__ = "project_member"

    id: Mapped[intpk]
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"))
    member_name: Mapped[str30]
    position: Mapped[str50 | None]

    project: Mapped["Project"] = relationship(back_populates="members")
    member: Mapped["Member"] = relationship(back_populates="projects")