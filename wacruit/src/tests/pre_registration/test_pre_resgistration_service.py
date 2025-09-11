from typing import List

import pytest

from wacruit.src.apps.pre_registration.exceptions import PreRegistAlreadyExistException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotActiveException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotExistException
from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.apps.pre_registration.schemas import PreRegistrationResponse
from wacruit.src.apps.pre_registration.services import PreRegistrationService


def test_create_pre_registration(
    pre_registration_service: PreRegistrationService, pre_registration_create_dto
):
    PreRegistration = pre_registration_service.create_pre_registration(
        pre_registration_create_dto
    )
    response = PreRegistrationResponse.from_orm(PreRegistration)

    assert response.url == "https://wafflestudio.com/24_5_pre_registration"
    assert response.generation == "24.5"
    assert response.is_active is True


def test_create_multiple_active_pre_registration(
    pre_registration_service: PreRegistrationService, pre_registration_create_dto
):
    pre_registration_service.create_pre_registration(pre_registration_create_dto)
    with pytest.raises(PreRegistAlreadyExistException):
        new_request = pre_registration_create_dto.copy()
        pre_registration_service.create_pre_registration(new_request)


def test_active_pre_registration(
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
    created_no_active_pre_registration: PreRegistration,
):
    response = pre_registration_service.get_active_pre_registration()

    assert response.url == "https://wafflestudio.com/24_5_pre_registration"
    assert response.generation == "24.5"
    assert response.is_active is True


def test_no_active_pre_registration(
    pre_registration_service: PreRegistrationService,
    created_no_active_pre_registration: PreRegistration,
):
    with pytest.raises(PreRegistNotActiveException):
        response = pre_registration_service.get_active_pre_registration()


def test_get_all_pre_registrations(
    pre_registration_service: PreRegistrationService,
    created_pre_registration_list: List[PreRegistration],
):
    response = pre_registration_service.get_pre_registration()
    assert len(response) == len(created_pre_registration_list)
    for i in range(5):
        assert response[i].generation == created_pre_registration_list[i].generation
        assert response[i].url == created_pre_registration_list[i].url
        assert response[i].is_active == created_pre_registration_list[i].is_active


def test_update_pre_registration(
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
    pre_registration_update_dto,
):
    PreRegistration = pre_registration_service.update_pre_registration(
        created_active_pre_registration.id, pre_registration_update_dto
    )

    response = PreRegistrationResponse.from_orm(PreRegistration)

    assert response.url == "https://wafflestudio.com/23_5_pre_registration"
    assert response.generation == "23.5"
    assert response.is_active is False


def test_delete_pre_registration_success(
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
):
    pre_registration_service.delete_pre_registration(created_active_pre_registration.id)

    with pytest.raises(PreRegistNotActiveException):
        pre_registration_service.get_active_pre_registration()


def test_delete_pre_registration_not_exist(
    pre_registration_service: PreRegistrationService,
):
    with pytest.raises(PreRegistNotExistException):
        pre_registration_service.delete_pre_registration(999)
