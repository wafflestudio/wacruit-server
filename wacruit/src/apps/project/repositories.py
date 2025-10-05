from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.models import ProjectImage
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
                joinedload(Project.images),
            )
            .filter(Project.id == project_id)
            .first()
        )

    def get_project_by_name(self, name: str) -> Project | None:
        return self.session.query(Project).filter(Project.name == name).first()

    def get_projects(self, offset: int = 0, limit: int = 10) -> list[Project]:
        # formed_at이 작은 순서대로 정렬
        return (
            self.session.query(Project)
            .order_by(Project.formed_at)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create_project(self, project: Project) -> Project:
        with self.transaction:
            self.session.add(project)
        return project

    def update_project(self, project: Project) -> Project:
        with self.transaction:
            self.session.merge(project)

        return project

    def get_project_image_by_id(self, image_id: int) -> ProjectImage | None:
        return (
            self.session.query(ProjectImage).filter(ProjectImage.id == image_id).first()
        )

    def get_project_images_by_project_id(self, project_id: int) -> list[ProjectImage]:
        return (
            self.session.query(ProjectImage)
            .filter(ProjectImage.project_id == project_id)
            .all()
        )

    def update_project_image(self, project_image_id: int) -> None:
        with self.transaction:
            query = (
                update(ProjectImage)
                .where(ProjectImage.id == project_image_id)
                .values(is_uploaded=True)
            )
            self.session.execute(query)

    def delete_project_image(self, project_image_id: int) -> None:
        with self.transaction:
            project_image = (
                self.session.query(ProjectImage)
                .filter(ProjectImage.id == project_image_id)
                .first()
            )
            if project_image:
                self.session.delete(project_image)
