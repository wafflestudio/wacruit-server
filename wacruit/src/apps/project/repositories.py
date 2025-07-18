from fastapi import Depends
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.models import ProjectImageURL
from wacruit.src.apps.project.models import ProjectURL
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class ProjectRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_project_by_id(self, project_id: int) -> Project | None:
        return (
            self.session.query(Project)
            .options(
                joinedload(Project.urls),
                joinedload(Project.image_urls),
            )
            .filter(Project.id == project_id)
            .first()
        )

    def get_project_by_name(self, name: str) -> Project | None:
        return self.session.query(Project).filter(Project.name == name).first()

    def get_projects(self, offset: int = 0, limit: int = 10) -> list[Project]:
        return self.session.query(Project).offset(offset).limit(limit).all()

    def create_project(self, project: Project) -> Project:
        with self.transaction:
            self.session.add(project)
        return project

    def update_project(self, project: Project) -> Project:
        with self.transaction:
            self.session.merge(project)

        return project
