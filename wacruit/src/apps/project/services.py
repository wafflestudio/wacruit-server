from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from wacruit.src.apps.common.enums import ProjectType
from wacruit.src.apps.common.exceptions import InvalidProjectTypeException
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.member.exceptions import MemberAlreadyExistsException
from wacruit.src.apps.member.exceptions import MemberNotFoundException
from wacruit.src.apps.member.repositories import MemberRepository
from wacruit.src.apps.project.exceptions import ProjectAlreadyExistsException
from wacruit.src.apps.project.exceptions import ProjectNotFoundException
from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.models import ProjectImageURL
from wacruit.src.apps.project.models import ProjectURL
from wacruit.src.apps.project.repositories import ProjectRepository
from wacruit.src.apps.project.schemas import ProjectBriefResponse
from wacruit.src.apps.project.schemas import ProjectCreateRequest
from wacruit.src.apps.project.schemas import ProjectDetailResponse
from wacruit.src.apps.project.schemas import ProjectLinkDto
from wacruit.src.apps.project.schemas import ProjectUpdateRequest


class ProjectService:
    def __init__(
        self,
        member_repository: MemberRepository = Depends(),
        project_repository: ProjectRepository = Depends(),
    ) -> None:
        self.member_repository = member_repository
        self.project_repository = project_repository

    def create_project(self, request: ProjectCreateRequest):
        if self.project_repository.get_project_by_name(request.name):
            raise ProjectAlreadyExistsException

        project = Project(
            name=request.name,
            summary=request.summary,
            introduction=request.introduction,
            thumbnail_url=request.thumbnail_url,
            project_type=request.project_type,
            is_active=request.is_active,
        )

        # 프로젝트를 먼저 생성하여 project_id를 얻음
        created_project = self.project_repository.create_project(project)

        # 프로젝트가 생성된 후 이미지와 URL 추가
        if request.images:
            if created_project.image_urls is None:
                created_project.image_urls = []
            for image_url in request.images:
                image_obj = ProjectImageURL(
                    project_id=created_project.id, url=image_url
                )
                created_project.image_urls.append(image_obj)

        if request.urls:
            if created_project.urls is None:
                created_project.urls = []
            for url_dto in request.urls:
                url_obj = ProjectURL(
                    project_id=created_project.id,
                    url_type=url_dto.url_type,
                    url=url_dto.url,
                )
                created_project.urls.append(url_obj)

        # 이미지와 URL이 추가된 프로젝트를 업데이트
        if request.images or request.urls:
            created_project = self.project_repository.update_project(created_project)

    def get_project(self, project_id: int) -> ProjectDetailResponse:
        project = self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundException
        return ProjectDetailResponse.from_orm(project)

    def list_projects(
            self, offset: int = 0, limit: int = 10
    ) -> ListResponse[ProjectBriefResponse]:
        projects = self.project_repository.get_projects(offset=offset, limit=limit)
        items = []
        for project in projects:
            items.append(ProjectBriefResponse.from_orm(project))
        return ListResponse(items=items)

    def update_project(
        self, project_id: int, request: ProjectUpdateRequest
    ) -> ProjectDetailResponse:
        project = self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundException
        for key, value in request.dict(exclude_none=True).items():
            setattr(project, key, value)
        updated_project = self.project_repository.update_project(project)
        if not updated_project:
            raise ProjectNotFoundException
        return ProjectDetailResponse.from_orm(updated_project)
