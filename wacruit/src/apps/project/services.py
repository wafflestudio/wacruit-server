from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.member.repositories import MemberRepository
from wacruit.src.apps.portfolio.file.aws.config import s3_config
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.file.aws.s3.method import S3PresignedUrlMethod
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_post_url
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_url
from wacruit.src.apps.project.exceptions import ProjectAlreadyExistsException
from wacruit.src.apps.project.exceptions import ProjectImageNotFoundException
from wacruit.src.apps.project.exceptions import ProjectNotFoundException
from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.models import ProjectImage
from wacruit.src.apps.project.models import ProjectURL
from wacruit.src.apps.project.repositories import ProjectRepository
from wacruit.src.apps.project.schemas import PresignedUrlWithIdResponse
from wacruit.src.apps.project.schemas import ProjectBriefResponse
from wacruit.src.apps.project.schemas import ProjectCreateRequest
from wacruit.src.apps.project.schemas import ProjectDetailResponse
from wacruit.src.apps.project.schemas import ProjectImageResponse
from wacruit.src.apps.project.schemas import ProjectUpdateRequest

_1_MIN = 60
_10_MIN = 10 * _1_MIN
_1_MB = 1024 * 1024
_50_MB = 50 * _1_MB


class ProjectService:
    def __init__(
        self,
        member_repository: MemberRepository = Depends(),
        project_repository: ProjectRepository = Depends(),
    ) -> None:
        self._s3_config = s3_config
        self._s3_client = S3Client(region_name=self._s3_config.bucket_region)
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
        if request.urls:
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

    def get_project_object_name(self, project_id: int, file_name: str) -> str:
        return f"PROJECT/{project_id}/{file_name}"

    def generate_presigned_url_for_post_image(
        self, project_id: int, file_name: str
    ) -> PresignedUrlWithIdResponse:
        project = self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundException
        object_name = self.get_project_object_name(project_id, file_name)
        url, fields = generate_presigned_post_url(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_object=object_name,
            expires_in=_10_MIN,
            conditions=[
                ["content-length-range", 0, _50_MB],
            ],
        )
        project_image = ProjectImage(
            project_id=project_id,
            object_key=object_name,
        )
        if project.images is None:
            project.images = []
        project.images.append(project_image)
        self.project_repository.update_project(project)
        return PresignedUrlWithIdResponse(
            object_name=object_name,
            presigned_url=url,
            fields=fields,
            project_image_id=project_image.id,
        )

    def generate_presigned_url_for_get_image(
        self, file_id: int
    ) -> PresignedUrlWithIdResponse:
        project_image = self.project_repository.get_project_image_by_id(file_id)
        if not project_image or not project_image.is_uploaded:
            raise ProjectImageNotFoundException
        object_name = project_image.object_key
        url = generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=S3PresignedUrlMethod.GET,
            method_parameters={
                "Bucket": self._s3_config.bucket_name,
                "Key": object_name,
            },
            expires_in=_10_MIN,
        )
        return PresignedUrlWithIdResponse(
            object_name=object_name,
            presigned_url=url,
            project_image_id=project_image.id,
        )

    def register_project_image_info_in_db(self, file_id: int) -> ProjectImageResponse:
        project_image = self.project_repository.get_project_image_by_id(file_id)
        if not project_image:
            raise ProjectImageNotFoundException
        self.project_repository.update_project_image(
            project_image_id=file_id,
        )
        project_image = self.project_repository.get_project_image_by_id(file_id)
        return ProjectImageResponse.from_orm(project_image)
