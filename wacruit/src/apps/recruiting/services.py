from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.schemas import RecruitingApplicantDto
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.user.models import User


class RecruitingService:
    def __init__(
        self,
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
    ):
        self.recruiting_repository = recruiting_repository

    def get_all_recruiting(self) -> ListResponse[RecruitingApplicantDto]:
        recruitings = self.recruiting_repository.get_all_recruitings()
        return ListResponse(items=RecruitingApplicantDto.from_orm_all(recruitings))

    def get_recruiting_by_id(
        self, recruiting_id: int, user: User
    ) -> RecruitingResponse:
        recruiting = self.recruiting_repository.get_recruiting_by_id(
            recruiting_id, user.id
        )
        if recruiting is None:
            raise RecruitingNotFoundException()

        problems = []
        for problem in recruiting.problems:
            status = 0
            if problem.submissions:
                status = problem.submissions[0].status.value
                for submission in problem.submissions:
                    if submission.status == CodeSubmissionStatus.SOLVED:
                        status = CodeSubmissionStatus.SOLVED.value
                        break
            problems.append({"num": problem.num, "status": status})

        return RecruitingResponse(
            name=recruiting.name,
            is_active=recruiting.is_active,
            from_date=recruiting.from_date,
            to_date=recruiting.to_date,
            description=recruiting.description,
            problems=problems,
        )
