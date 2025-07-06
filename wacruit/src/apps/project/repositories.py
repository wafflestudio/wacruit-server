from fastapi import Depends
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.models import ProjectImageURL
from wacruit.src.apps.project.models import ProjectMember
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
                joinedload(Project.leader),
                joinedload(Project.urls),
                joinedload(Project.image_urls),
            )
            .filter(Project.id == project_id)
            .first()
        )

    def get_project_by_name(self, name: str) -> Project | None:
        return self.session.query(Project).filter(Project.name == name).first()

    def get_projects(self) -> list[Project]:
        return self.session.query(Project).all()

    def get_member_by_id(self, project_id, member_id: int) -> ProjectMember | None:
        return (
            self.session.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.member_id == member_id,
            )
            .first()
        )

    def create_project(self, project: Project) -> Project:
        with self.transaction:
            self.session.add(project)
        return project

    def update_project(self, project: Project) -> Project:
        with self.transaction:
            self.session.merge(project)

        return project

    def add_member_to_project(self, project: Project, member: ProjectMember):
        with self.transaction:
            project.members.append(member)
            self.session.add(project)

    def delete_member_from_project(self, project: Project, member: ProjectMember):
        with self.transaction:
            project.members.remove(member)
            self.session.add(project)
