from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.project.schemas import PresignedUrlWithIdResponse
from wacruit.src.apps.project.schemas import ProjectBriefResponse
from wacruit.src.apps.project.schemas import ProjectCreateRequest
from wacruit.src.apps.project.schemas import ProjectDetailResponse
from wacruit.src.apps.project.schemas import ProjectImageResponse
from wacruit.src.apps.project.schemas import ProjectImageUploadRequest
from wacruit.src.apps.project.schemas import ProjectUpdateRequest
from wacruit.src.apps.project.services import ProjectService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/projects", tags=["projects"])


@v3_router.post("", status_code=HTTPStatus.CREATED)
def create_project(
    request: ProjectCreateRequest,
    project_service: Annotated[ProjectService, Depends()],
    admin_user: AdminUser,
):
    project_service.create_project(request)


@v3_router.get("/{project_id}")
def get_project(
    project_id: int, project_service: Annotated[ProjectService, Depends()]
) -> ProjectDetailResponse:
    return project_service.get_project(project_id)


@v3_router.get("")
def list_projects(
    project_service: Annotated[ProjectService, Depends()],
    offset: int = 0,
    limit: int = 10,
) -> ListResponse[ProjectBriefResponse]:
    return project_service.list_projects(offset=offset, limit=limit)


@v3_router.patch("/{project_id}")
def update_project(
    admin_user: AdminUser,
    project_id: int,
    request: ProjectUpdateRequest,
    project_service: Annotated[ProjectService, Depends()],
) -> ProjectDetailResponse:
    return project_service.update_project(project_id, request)


@v3_router.post("/image/upload")
def get_upload_project_image_url(
    admin_user: AdminUser,
    request: ProjectImageUploadRequest,
    project_service: Annotated[ProjectService, Depends()],
) -> PresignedUrlWithIdResponse:
    return project_service.generate_presigned_url_for_post_image(
        project_id=request.project_id, file_name=request.file_name
    )


@v3_router.get("/image/download/{file_id}")
def get_download_project_image_url(
    admin_user: AdminUser,
    file_id: int,
    project_service: Annotated[ProjectService, Depends()],
) -> PresignedUrlWithIdResponse:
    return project_service.generate_presigned_url_for_get_image(file_id=file_id)


@v3_router.get("/image/check-upload-completed/{file_id}")
def check_upload_project_image_completed(
    admin_user: AdminUser,
    file_id: int,
    project_service: Annotated[ProjectService, Depends()],
) -> ProjectImageResponse:
    return project_service.register_project_image_info_in_db(file_id=file_id)
