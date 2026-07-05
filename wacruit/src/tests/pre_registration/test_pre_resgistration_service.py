from typing import List
from typing import cast

from pydantic import EmailStr
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from wacruit.src.apps.pre_registration.exceptions import PreRegistAlreadyExistException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotActiveException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotExistException
from wacruit.src.apps.pre_registration.exceptions import (
    PreRegistUserAlreadyExistException,
)
from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.apps.pre_registration.models import PreRegistrationUser
from wacruit.src.apps.pre_registration.schemas import CreatePreRegistrationUserRequest
from wacruit.src.apps.pre_registration.schemas import PreRegistrationResponse
from wacruit.src.apps.pre_registration.schemas import SendPreRegistrationEmailRequest
from wacruit.src.apps.pre_registration.schemas import UpdatePreRegistrationRequest
from wacruit.src.apps.pre_registration.services import PreRegistrationService
from wacruit.src.tests.pre_registration.conftest import FakeEmailService


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
        pre_registration_service.get_active_pre_registration()


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


def test_update_active_pre_registration_itself(
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
):
    request = UpdatePreRegistrationRequest(
        url="https://wafflestudio.com/24_5_pre_registration_updated",
        generation="24.5",
        is_active=True,
    )

    pre_registration = pre_registration_service.update_pre_registration(
        created_active_pre_registration.id, request
    )

    assert (
        pre_registration.url == "https://wafflestudio.com/24_5_pre_registration_updated"
    )
    assert pre_registration.generation == "24.5"
    assert pre_registration.is_active is True


def test_update_pre_registration_to_active_when_other_active_exists(
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
    created_no_active_pre_registration: PreRegistration,
):
    request = UpdatePreRegistrationRequest(is_active=True)

    with pytest.raises(PreRegistAlreadyExistException):
        pre_registration_service.update_pre_registration(
            created_no_active_pre_registration.id, request
        )


def test_pre_registration_active_key_unique_constraint(
    db_session: Session,
    created_active_pre_registration: PreRegistration,
):
    duplicated_active_pre_registration = PreRegistration(
        url="https://wafflestudio.com/25_5_pre_registration",
        generation="25.5",
        is_active=True,
    )

    db_session.add(duplicated_active_pre_registration)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_create_pre_registration_user(
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
):
    request = CreatePreRegistrationUserRequest(
        name="Waffle User",
        email=cast(EmailStr, "waffle@example.com"),
        phone_number="010-1234-5678",
        university="Seoul National University",
        college="Engineering",
        department="Computer Science",
    )

    response = pre_registration_service.create_pre_registration_user(request)

    assert response.pre_registration_id == created_active_pre_registration.id
    assert response.name == "Waffle User"
    assert response.email == "waffle@example.com"
    assert response.phone_number == "010-1234-5678"
    assert response.university == "Seoul National University"
    assert response.college == "Engineering"
    assert response.department == "Computer Science"


def test_create_pre_registration_user_without_active(
    pre_registration_service: PreRegistrationService,
    created_no_active_pre_registration: PreRegistration,
):
    request = CreatePreRegistrationUserRequest(
        name="Waffle User",
        email=cast(EmailStr, "waffle@example.com"),
        phone_number="010-1234-5678",
    )

    with pytest.raises(PreRegistNotActiveException):
        pre_registration_service.create_pre_registration_user(request)


def test_create_duplicate_pre_registration_user(
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
):
    request = CreatePreRegistrationUserRequest(
        name="Waffle User",
        email=cast(EmailStr, "waffle@example.com"),
        phone_number="010-1234-5678",
    )

    pre_registration_service.create_pre_registration_user(request)
    with pytest.raises(PreRegistUserAlreadyExistException):
        pre_registration_service.create_pre_registration_user(request)


def test_get_active_pre_registration_users(
    db_session: Session,
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
    created_no_active_pre_registration: PreRegistration,
):
    active_user = PreRegistrationUser(
        pre_registration_id=created_active_pre_registration.id,
        name="Active User",
        email="active@example.com",
        phone_number="010-1111-1111",
    )
    inactive_user = PreRegistrationUser(
        pre_registration_id=created_no_active_pre_registration.id,
        name="Inactive User",
        email="inactive@example.com",
        phone_number="010-2222-2222",
    )
    db_session.add_all([active_user, inactive_user])
    db_session.commit()

    response = pre_registration_service.get_pre_registration_users(
        pre_registration_id=None,
        active_only=True,
        limit=50,
        offset=0,
    )

    assert len(response) == 1
    assert response[0].pre_registration_id == created_active_pre_registration.id
    assert response[0].email == "active@example.com"


def test_get_pre_registration_users_by_pre_registration_id(
    db_session: Session,
    pre_registration_service: PreRegistrationService,
    created_active_pre_registration: PreRegistration,
    created_no_active_pre_registration: PreRegistration,
):
    active_user = PreRegistrationUser(
        pre_registration_id=created_active_pre_registration.id,
        name="Active User",
        email="active@example.com",
        phone_number="010-1111-1111",
    )
    inactive_user = PreRegistrationUser(
        pre_registration_id=created_no_active_pre_registration.id,
        name="Inactive User",
        email="inactive@example.com",
        phone_number="010-2222-2222",
    )
    db_session.add_all([active_user, inactive_user])
    db_session.commit()

    response = pre_registration_service.get_pre_registration_users(
        pre_registration_id=created_no_active_pre_registration.id,
        active_only=False,
        limit=50,
        offset=0,
    )

    assert len(response) == 1
    assert response[0].pre_registration_id == created_no_active_pre_registration.id
    assert response[0].email == "inactive@example.com"


def test_send_email_to_active_pre_registration_users(
    db_session: Session,
    pre_registration_service: PreRegistrationService,
    fake_email_service: FakeEmailService,
    created_active_pre_registration: PreRegistration,
    created_no_active_pre_registration: PreRegistration,
):
    active_user = PreRegistrationUser(
        pre_registration_id=created_active_pre_registration.id,
        name="Active User",
        email="active@example.com",
        phone_number="010-1111-1111",
    )
    inactive_user = PreRegistrationUser(
        pre_registration_id=created_no_active_pre_registration.id,
        name="Inactive User",
        email="inactive@example.com",
        phone_number="010-2222-2222",
    )
    db_session.add_all([active_user, inactive_user])
    db_session.commit()

    response = pre_registration_service.send_email_to_pre_registration_users(
        SendPreRegistrationEmailRequest(
            active_only=True,
            subject="subject",
            content="content",
            html_content="<p>content</p>",
        )
    )

    assert response.total_count == 1
    assert response.success_count == 1
    assert response.failed_count == 0
    assert response.failed_emails == []
    assert fake_email_service.sent_emails == [
        ("active@example.com", "subject", "content", "<p>content</p>")
    ]


def test_send_email_to_pre_registration_users_returns_failed_emails(
    db_session: Session,
    pre_registration_service: PreRegistrationService,
    fake_email_service: FakeEmailService,
    created_active_pre_registration: PreRegistration,
):
    first_user = PreRegistrationUser(
        pre_registration_id=created_active_pre_registration.id,
        name="First User",
        email="first@example.com",
        phone_number="010-1111-1111",
    )
    second_user = PreRegistrationUser(
        pre_registration_id=created_active_pre_registration.id,
        name="Second User",
        email="second@example.com",
        phone_number="010-2222-2222",
    )
    db_session.add_all([first_user, second_user])
    db_session.commit()
    fake_email_service.failed_emails.add("second@example.com")

    response = pre_registration_service.send_email_to_pre_registration_users(
        SendPreRegistrationEmailRequest(
            active_only=True,
            subject="subject",
            content="content",
        )
    )

    expected_total_count = 2

    assert response.total_count == expected_total_count
    assert response.success_count == 1
    assert response.failed_count == 1
    assert response.failed_emails == ["second@example.com"]
    assert fake_email_service.sent_emails == [
        ("first@example.com", "subject", "content", None)
    ]
