from typing import Sequence

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.resume.exceptions import ResumeNotFound
from wacruit.src.apps.resume.schemas import ResumeQuestionDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.schemas import UserResumeSubmissionDto
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.dependencies import CurrentUser
from wacruit.src.apps.user.exceptions import UserPermissionDeniedException

v1_router = APIRouter(prefix="/v1/recruiting", tags=["resume"])


@v1_router.get(
    "/{recruiting_id}/questions",
    responses=responses_from(UserPermissionDeniedException),
)
def get_questions(
    current_user: CurrentUser,
    recruiting_id: int,
    resume_service: ResumeService = Depends(),
) -> ListResponse[ResumeQuestionDto]:
    questions = resume_service.get_questions_by_recruiting_id(recruiting_id)
    return ListResponse(items=questions)


@v1_router.get(
    "/{recruiting_id}/resumes", responses=responses_from(UserPermissionDeniedException)
)
def get_my_resumes(
    current_user: CurrentUser,
    recruiting_id: int,
    resume_service: ResumeService = Depends(),
) -> ListResponse[UserResumeSubmissionDto]:
    resumes = resume_service.get_resumes_by_user_and_recruiting_id(
        current_user.id, recruiting_id
    )
    return ListResponse(items=resumes)


@v1_router.post(
    "/{recruiting_id}/resumes",
    responses=responses_from(ResumeNotFound, UserPermissionDeniedException),
)
def create_resume(
    current_user: CurrentUser,
    recruiting_id: int,
    answers: Sequence[ResumeSubmissionCreateDto],
    resume_service: ResumeService = Depends(),
) -> ListResponse[UserResumeSubmissionDto]:
    created_items = resume_service.create_resume(
        current_user.id, recruiting_id, answers
    )
    return ListResponse(items=created_items)


@v1_router.put(
    "/{recruiting_id}/resumes",
    responses=responses_from(ResumeNotFound, UserPermissionDeniedException),
)
def update_resume(
    current_user: CurrentUser,
    recruiting_id: int,
    request: Sequence[ResumeSubmissionCreateDto],
    resume_service: ResumeService = Depends(),
) -> ListResponse[UserResumeSubmissionDto]:
    updated_items = resume_service.update_resumes(
        current_user.id, recruiting_id, request
    )
    return ListResponse(items=updated_items)


@v1_router.delete(
    "/{recruiting_id}/resumes",
    status_code=204,
    responses=responses_from(UserPermissionDeniedException),
)
def withdraw_resume(
    current_user: CurrentUser,
    recruiting_id: int,
    resume_service: ResumeService = Depends(),
):
    """
    유저가 제출한 모든 이력서를 삭제하고 관련 정보를 초기화합니다.
    이 작업은 되돌릴 수 없으므로 사전에 유저에게 확인을 받아야 합니다.
    """
    resume_service.withdraw_resume(current_user.id, recruiting_id)
    return Response(status_code=204)
