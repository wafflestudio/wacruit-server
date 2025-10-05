from typing import Annotated, cast, TYPE_CHECKING

from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.member.repositories import MemberRepository
from wacruit.src.apps.portfolio.file.aws.config import s3_config
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.file.aws.s3.method import S3PresignedUrlMethod
from wacruit.src.apps.portfolio.file.aws.s3.utils import delete_object
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_post_url
from wacruit.src.apps.portfolio.file.aws.s3.utils import generate_presigned_url
from wacruit.src.apps.project.exceptions import GetPresignedURLException
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
from wacruit.src.apps.project.schemas import ProjectLinkDto
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
            project_type=request.project_type,
            formed_at=request.formed_at,
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

        # URL이 추가된 프로젝트를 업데이트
        if request.urls:
            created_project = self.project_repository.update_project(created_project)

    def get_project(self, project_id: int) -> ProjectDetailResponse:
        project = self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundException
        images = []
        thumbnail_image = None
        if project.images is not None:
            for image in project.images:
                if not image.is_uploaded:
                    continue
                try:
                    presigned_url = self.generate_presigned_url_for_get_image(image.id)
                    dto = PresignedUrlWithIdResponse(
                        object_name=image.object_key,
                        presigned_url=presigned_url,
                        project_image_id=image.id,
                    )
                    if image.is_thumbnail and thumbnail_image is None:
                        thumbnail_image = dto
                    else:
                        images.append(dto)
                except Exception as exc:
                    raise GetPresignedURLException() from exc

        return ProjectDetailResponse(
            id=project.id,
            name=project.name,
            summary=project.summary,
            introduction=project.introduction,
            thumbnail_image=thumbnail_image,
            project_type=project.project_type,
            formed_at=project.formed_at,
            is_active=project.is_active,
            images=images,
            urls=[
                ProjectLinkDto(url_type=url.url_type, url=url.url)
                for url in project.urls
            ]
            if project.urls
            else None,
        )

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

        # urls는 별도로 처리
        request_dict = request.dict(exclude_none=True)
        urls_data = request_dict.pop("urls", None)

        for key, value in request_dict.items():
            setattr(project, key, value)

        if urls_data is not None:
            if project.urls is None:
                project.urls = []
            for url_dto in urls_data:
                url_obj = ProjectURL(
                    project_id=project.id,
                    url_type=url_dto["url_type"],
                    url=url_dto["url"],
                )
                project.urls.append(url_obj)

        updated_project = self.project_repository.update_project(project)
        if not updated_project:
            raise ProjectNotFoundException
        images = []
        thumbnail_image = None
        if updated_project.images is not None:
            for image in updated_project.images:
                if not image.is_uploaded:
                    continue
                try:
                    presigned_url = self.generate_presigned_url_for_get_image(image.id)
                    dto = PresignedUrlWithIdResponse(
                        object_name=image.object_key,
                        presigned_url=presigned_url,
                        project_image_id=image.id,
                    )
                    if image.is_thumbnail and thumbnail_image is None:
                        thumbnail_image = dto
                    else:
                        images.append(dto)
                except Exception as exc:
                    raise GetPresignedURLException() from exc

        return ProjectDetailResponse(
            id=updated_project.id,
            name=updated_project.name,
            summary=updated_project.summary,
            introduction=updated_project.introduction,
            thumbnail_image=thumbnail_image,
            project_type=updated_project.project_type,
            formed_at=updated_project.formed_at,
            is_active=updated_project.is_active,
            images=images,
            urls=[
                ProjectLinkDto(url_type=url.url_type, url=url.url)
                for url in updated_project.urls
            ]
            if updated_project.urls
            else None,
        )

    def get_project_image_object_name(self, project_id: int, file_name: str) -> str:
        return f"PROJECT/{project_id}/{file_name}"

    def get_project_thumbnail_object_name(self, project_id: int, file_name: str) -> str:
        return f"PROJECT/{project_id}/thumbnail/{file_name}"

    def generate_presigned_url_for_post_image(
        self, project_id: int, file_name: str, is_thumbnail: bool = False
    ) -> PresignedUrlWithIdResponse:
        project = self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundException
        if is_thumbnail:
            object_name = self.get_project_thumbnail_object_name(project_id, file_name)
        else:
            object_name = self.get_project_image_object_name(project_id, file_name)
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
            is_thumbnail=is_thumbnail,
        )
        if project.images is None:
            project.images = []
        # 썸네일을 업로드하려는 경우 기존 썸네일 플래그 해제
        if is_thumbnail:
            for img in project.images:
                if img.is_thumbnail:
                    img.is_thumbnail = False
        project.images.append(project_image)
        self.project_repository.update_project(project)

        return PresignedUrlWithIdResponse(
            object_name=object_name,
            presigned_url=url,
            fields=fields,
            project_image_id=project_image.id,
        )

    def generate_presigned_url_for_get_image(self, file_id: int) -> str:
        project_image = self.project_repository.get_project_image_by_id(file_id)
        if not project_image or not project_image.is_uploaded:
            raise ProjectImageNotFoundException
        object_name = project_image.object_key
        return self._generate_presigned_url_for_get_object(object_name)

    def _generate_presigned_url_for_get_object(self, object_key: str) -> str:
        return generate_presigned_url(
            s3_client=self._s3_client.client,
            client_method=S3PresignedUrlMethod.GET,
            method_parameters={
                "Bucket": self._s3_config.bucket_name,
                "Key": object_key,
            },
            expires_in=_10_MIN,
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

    def update_project_image(self, file_id: int) -> PresignedUrlWithIdResponse:
        project_image = self.project_repository.get_project_image_by_id(file_id)
        if not project_image:
            raise ProjectImageNotFoundException

        url, fields = generate_presigned_post_url(
            s3_client=self._s3_client.client,
            s3_bucket=self._s3_config.bucket_name,
            s3_object=project_image.object_key,
            expires_in=_10_MIN,
            conditions=[["content-length-range", 0, _50_MB]],
        )
        return PresignedUrlWithIdResponse(
            object_name=project_image.object_key,
            presigned_url=url,
            fields=fields,
            project_image_id=project_image.id,
        )

    def delete_project_image(self, file_id: int) -> None:
        project_image = self.project_repository.get_project_image_by_id(file_id)
        if not project_image:
            raise ProjectImageNotFoundException
        object_name = project_image.object_key
        # S3에서 삭제
        delete_object(self._s3_client.client, self._s3_config.bucket_name, object_name)
        # DB에서 삭제
        self.project_repository.delete_project_image(file_id)
