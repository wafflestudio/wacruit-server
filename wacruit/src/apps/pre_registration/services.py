from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.pre_registration.exceptions import PreRegistAlreadyExistException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotActiveException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotExistException
from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.apps.pre_registration.repositories import PreRegistrationRepository
from wacruit.src.apps.pre_registration.schemas import CreatePreRegistrationRequest
from wacruit.src.apps.pre_registration.schemas import UpdatePreRegistrationRequest


class PreRegistrationService:
    def __init__(
        self,
        pre_registration_repository: Annotated[PreRegistrationRepository, Depends()],
    ):
        self.pre_registration_repository = pre_registration_repository

    def check_active_pre_registration(self) -> bool:
        pre_registration = (
            self.pre_registration_repository.get_active_pre_registration()
        )
        if pre_registration is None:
            return False
        return True

    def get_active_pre_registration(self) -> PreRegistration:
        pre_registration = (
            self.pre_registration_repository.get_active_pre_registration()
        )
        if pre_registration is None:
            raise PreRegistNotActiveException
        return pre_registration

    def get_pre_registration(self) -> list[PreRegistration]:
        pre_registration_list = self.pre_registration_repository.get_pre_registration()
        return pre_registration_list

    def create_pre_registration(
        self, req: CreatePreRegistrationRequest
    ) -> PreRegistration:
        if req.is_active and (self.check_active_pre_registration()):
            raise PreRegistAlreadyExistException
        to_create = PreRegistration(
            url=req.url, generation=req.generation, is_active=req.is_active
        )
        pre_registration = self.pre_registration_repository.create_pre_registration(
            to_create
        )
        return pre_registration

    def update_pre_registration(
        self, pre_registration_id: int, req: UpdatePreRegistrationRequest
    ) -> PreRegistration:
        pre_registration = self.pre_registration_repository.get_pre_registration_by_id(
            pre_registration_id
        )
        if pre_registration is None:
            raise PreRegistNotExistException
        if req.is_active and (self.check_active_pre_registration()):
            raise PreRegistAlreadyExistException

        for key, value in req.dict(exclude_none=True).items():
            setattr(pre_registration, key, value)
        return self.pre_registration_repository.update_pre_registration(
            pre_registration
        )

    def delete_pre_registration(self, pre_registration_id: int) -> None:
        pre_registration = self.pre_registration_repository.get_pre_registration_by_id(
            pre_registration_id
        )
        if pre_registration is None:
            raise PreRegistNotExistException
        self.pre_registration_repository.delete_pre_registration(pre_registration_id)
