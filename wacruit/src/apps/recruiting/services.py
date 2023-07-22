from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.schemas import RecruitingListResponse


class RecruitingService:
    def __init__(
        self,
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
        problem_repository: Annotated[ProblemRepository, Depends()],
    ):
        self.recruiting_repository = recruiting_repository
        self.problem_repository = problem_repository

    def get_all_recruiting(self) -> ListResponse[RecruitingListResponse]:
        recruitings = self.recruiting_repository.get_all_recruitings()
        return ListResponse(items=RecruitingListResponse.from_orm_all(recruitings))
