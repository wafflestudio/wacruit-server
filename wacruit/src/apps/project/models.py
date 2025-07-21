from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.common.enums import ProjectType
from wacruit.src.apps.common.enums import ProjectURLType
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str50
from wacruit.src.database.base import str100
from wacruit.src.database.base import str255
from wacruit.src.database.base import str1500

if TYPE_CHECKING:
    from wacruit.src.apps.member.models import Member


class Project(DeclarativeBase):
    __tablename__ = "project"

    id: Mapped[intpk]
    name: Mapped[str30]
    summary: Mapped[str100 | None]
    introduction: Mapped[str1500 | None]
    thumbnail_url: Mapped[str255 | None]
    project_type: Mapped[ProjectType]
    is_active: Mapped[bool] = mapped_column(default=True)
    urls: Mapped[list["ProjectURL"] | None] = relationship(
        back_populates="source_project"
    )
    images: Mapped[list["ProjectImage"] | None] = relationship(
        back_populates="source_project"
    )


class ProjectURL(DeclarativeBase):
    __tablename__ = "project_url"

    id: Mapped[intpk]
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    url_type: Mapped[ProjectURLType]
    url: Mapped[str255]

    source_project: Mapped["Project"] = relationship(back_populates="urls")


class ProjectImage(DeclarativeBase):
    __tablename__ = "project_image"

    id: Mapped[intpk]
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    object_key: Mapped[str255]
    is_uploaded: Mapped[bool] = mapped_column(default=False)

    source_project: Mapped["Project"] = relationship(back_populates="images")
