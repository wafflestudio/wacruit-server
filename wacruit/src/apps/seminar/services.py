from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.seminar.exceptions import SeminarListEmptyException
from wacruit.src.apps.seminar.exceptions import SeminarNotActiveException
from wacruit.src.apps.seminar.exceptions import SeminarNotFoundException
from wacruit.src.apps.seminar.models import Seminar
from wacruit.src.apps.seminar.repositories import SeminarRepository
from wacruit.src.apps.seminar.schemas import CreateSeminarRequest
from wacruit.src.apps.seminar.schemas import UpdateSeminarRequest


class SeminarService:
    def __init__(self, seminar_repository: Annotated[SeminarRepository, Depends()]):
        self.seminar_repository = seminar_repository

    def get_seminar_by_id(self, seminar_id: int) -> Seminar:
        seminar = self.seminar_repository.get_seminar_by_id(seminar_id)
        if seminar is None:
            raise SeminarNotFoundException
        return seminar

    def get_active_seminar(self) -> list[Seminar]:
        seminar_list = self.seminar_repository.get_active_seminars()
        if not seminar_list:
            raise SeminarNotActiveException
        return seminar_list

    def get_all_seminars(self) -> list[Seminar]:
        seminar_list = self.seminar_repository.get_all_seminars()
        if not seminar_list:
            raise SeminarListEmptyException
        return seminar_list

    def create_seminar(self, request: CreateSeminarRequest) -> Seminar:
        seminar = Seminar(
            seminar_type=request.seminar_type,
            curriculum_info=request.curriculum_info,
            prerequisite_info=request.prerequisite_info,
            is_active=request.is_active,
        )

        created_seminar: Seminar = self.seminar_repository.create_seminar(seminar)

        return created_seminar

    def update_seminar(self, seminar_id: int, request: UpdateSeminarRequest) -> Seminar:
        seminar = self.seminar_repository.get_seminar_by_id(seminar_id)
        if seminar is None:
            raise SeminarNotFoundException
        for key, value in request.dict(exclude_none=True).items():
            setattr(seminar, key, value)

        updated_seminar = self.seminar_repository.update_seminar(seminar)

        return updated_seminar
