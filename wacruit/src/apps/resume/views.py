from typing import Sequence

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from wacruit.src.apps.common.dependencies import CurrentUser
from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.resume.exceptions import ResumeNotFound
from wacruit.src.apps.resume.schemas import ResumeListingByIdDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionWithUserDto
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.exceptions import UserPermissionDeniedException

v1_router = APIRouter(prefix="/v1/resumes", tags=["resume"])


@v1_router.get("/")
def list_resumes(
    current_user: CurrentUser,
    request: ResumeListingByIdDto,
    resume_service: ResumeService = Depends(),
) -> ListResponse[ResumeSubmissionWithUserDto]:
    if not current_user.is_admin:
        raise UserPermissionDeniedException

    resumes = resume_service.list_resumes(request.recruiting_id)
    return ListResponse(items=resumes)


@v1_router.get("/my")
def get_resume(
    current_user: CurrentUser,
    request: ResumeListingByIdDto,
    resume_service: ResumeService = Depends(),
) -> ListResponse[ResumeSubmissionWithUserDto]:
    resumes = resume_service.get_resumes(current_user.id, request.recruiting_id)
    return ListResponse(items=resumes)


@v1_router.post("/")
def create_resume(
    current_user: CurrentUser,
    request: Sequence[ResumeSubmissionCreateDto],
    resume_service: ResumeService = Depends(),
) -> list[ResumeSubmissionWithUserDto]:
    # TODO: Add permission check
    return resume_service.create_resume(current_user.id, request)


@v1_router.put("/", responses=responses_from(ResumeNotFound))
def update_resume(
    current_user: CurrentUser,
    request: Sequence[ResumeSubmissionCreateDto],
    resume_service: ResumeService = Depends(),
) -> list[ResumeSubmissionWithUserDto]:
    # TODO: Add permission check
    return resume_service.update_resumes(current_user.id, request)


@v1_router.delete("/", responses=responses_from(ResumeNotFound), status_code=204)
def delete_resume(
    current_user: CurrentUser,
    resume_service: ResumeService = Depends(),
):
    resume_service.delete_resume(current_user.id)
    return Response(status_code=204)
