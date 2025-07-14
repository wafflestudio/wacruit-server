from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.project.schemas import ProjectBriefResponse
from wacruit.src.apps.project.schemas import ProjectCreateRequest
from wacruit.src.apps.project.schemas import ProjectDetailResponse
from wacruit.src.apps.project.schemas import ProjectUpdateRequest
from wacruit.src.apps.project.services import ProjectService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/projects", tags=["projects"])


@v3_router.post("")
def create_project(
    request: ProjectCreateRequest,
    project_service: Annotated[ProjectService, Depends()],
    admin_user: AdminUser,
):
    return project_service.create_project(request)


@v3_router.get("/{project_id}")
def get_project(
    project_id: int, project_service: Annotated[ProjectService, Depends()]
) -> ProjectDetailResponse:
    return project_service.get_project(project_id)


@v3_router.get("")
def list_projects(
    project_service: Annotated[ProjectService, Depends()]
) -> ListResponse[ProjectBriefResponse]:
    return project_service.list_projects()


@v3_router.patch("/{project_id}")
def update_project(
    admin_user: AdminUser,
    project_id: int,
    request: ProjectUpdateRequest,
    project_service: Annotated[ProjectService, Depends()],
) -> ProjectDetailResponse:
    return project_service.update_project(project_id, request)


# @v3_router.post("/{project_id}/members")
# def add_project_member(
#     admin_user: AdminUser,
#     project_id: int,
#     request: ProjectMemberCreateRequest,
#     project_service: Annotated[ProjectService, Depends()],
# ):
#     return project_service.add_project_member(project_id, request)


# @v3_router.get("/{project_id}/members")
# def list_project_members(
#     project_id: int, project_service: Annotated[ProjectService, Depends()]
# ) -> ListResponse[ProjectMemberResponse]:
#     return project_service.list_project_members(project_id)


# @v3_router.patch("/{project_id}/members/{member_id}")
# def update_project_member(
#     admin_user: AdminUser,
#     project_id: int,
#     member_id: int,
#     request: ProjectMemberUpdateRequest,
#     project_service: Annotated[ProjectService, Depends()],
# ) -> ListResponse[ProjectMemberResponse]:
#     return project_service.update_project_member(project_id, member_id, request)


# @v3_router.delete("/{project_id}/members/{member_id}")
# def delete_project_member(
#     admin_user: AdminUser,
#     project_id: int,
#     member_id: int,
#     project_service: Annotated[ProjectService, Depends()],
# ) -> ListResponse[ProjectMemberResponse]:
#     return project_service.delete_project_member(project_id, member_id)
