from typing import Sequence

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.resume.exceptions import ResumeNotFound
from wacruit.src.apps.resume.schemas import ResumeListingByIdDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionWithUserDto
from wacruit.src.apps.resume.services import ResumeService

v1_router = APIRouter(prefix="/v1/resumes", tags=["resume"])


@v1_router.get("/")
async def list_resumes(
    request: ResumeListingByIdDto,
    resume_service: ResumeService = Depends(),
) -> ListResponse[ResumeSubmissionWithUserDto]:
    resumes = resume_service.list_resumes(request.recruiting_id)
    return ListResponse(items=resumes)


@v1_router.post("/")
async def create_resume(
    request: Sequence[ResumeSubmissionCreateDto],
    resume_service: ResumeService = Depends(),
) -> list[ResumeSubmissionWithUserDto]:
    # TODO: Add permission check
    return resume_service.create_resume(request)


@v1_router.put("/", responses=responses_from(ResumeNotFound))
async def update_resume(
    request: Sequence[ResumeSubmissionDto],
    resume_service: ResumeService = Depends(),
) -> list[ResumeSubmissionWithUserDto]:
    # TODO: Add permission check
    return resume_service.update_resumes(request)


@v1_router.delete("/{id}", responses=responses_from(ResumeNotFound), status_code=204)
async def delete_resume(
    id: int,
    resume_service: ResumeService = Depends(),
):
    resume_service.delete_resume(id)
    return Response(status_code=204)
