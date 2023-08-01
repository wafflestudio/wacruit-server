from typing import cast

from pydantic import EmailStr
import pytest
from sqlalchemy.exc import IntegrityError

from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.exceptions import UserNotFoundException
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.schemas import UserCreateRequest
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.schemas import UserUpdateRequest
from wacruit.src.apps.user.services import UserService


def test_create_user(user_service: UserService):
    request = UserCreateRequest(
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email=EmailStr("test@test.com"),
    )
    response = user_service.create_user("sso_id", request)
    assert response.id is not None


def test_create_user_duplicate_sso_id(user_service: UserService):
    sso_id = "test"
    request = UserCreateRequest(
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email=EmailStr("test2@test.com"),
    )
    user_service.create_user(sso_id, request)
    with pytest.raises(UserAlreadyExistsException):
        new_request = request.copy()
        user_service.create_user(sso_id, new_request)


def test_create_user_duplicate_email(user_service: UserService):
    sso_id = "test"
    request = UserCreateRequest(
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email=EmailStr("test@test.com"),
    )
    user_service.create_user(sso_id, request)
    with pytest.raises(UserAlreadyExistsException):
        new_request = request.copy()
        user_service.create_user(sso_id, new_request)


def test_update_user(created_user: User, user_service: UserService):
    updated_request = UserUpdateRequest(
        first_name="test2",
        last_name="test2",
        phone_number="010-0000-0001",
        email=EmailStr("test2@test.com"),
        department="test",
        college="test",
        university="test",
    )
    user_service.update_user(created_user, updated_request)
    assert created_user.first_name == updated_request.first_name
    assert created_user.last_name == updated_request.last_name
    assert created_user.phone_number == updated_request.phone_number
    assert created_user.department == updated_request.department
    assert created_user.college == updated_request.college
    assert created_user.university == updated_request.university


def test_update_user_duplicate_email(created_user: User, user_service: UserService):
    sso_id = "test"
    create_request = UserCreateRequest(
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email=EmailStr("test2@test.com"),
    )
    user_service.create_user(sso_id, create_request)
    with pytest.raises(IntegrityError):
        update_request = UserUpdateRequest(
            email=create_request.email,  # type: ignore
        )
        user_service.update_user(created_user, update_request)


def test_list_user_detail(user_service: UserService):
    sso_id = "test"
    request = UserCreateRequest(
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email=EmailStr("test@test.com"),
    )
    response = user_service.create_user(sso_id, request)
    assert response.id is not None

    users = user_service.list_users()
    assert len(users) == 1
    assert users[0].id == response.id
    assert users[0].sso_id == sso_id


def test_update_invitation_emails(created_user: User, user_service: UserService):
    request = UserUpdateInvitationEmailsRequest(
        github_email=EmailStr("github@mail.com"),
        notion_email=EmailStr("notion@mail.com"),
        slack_email=EmailStr("slack@smail.com"),
    )
    response = user_service.update_invitaion_emails(created_user, request)
    assert response.github_email == request.github_email
    assert response.notion_email == request.notion_email
    assert response.slack_email == request.slack_email


def test_update_invitation_emails_user_not_found(user_service: UserService, user: User):
    request = UserUpdateInvitationEmailsRequest(
        github_email=EmailStr("github@mail.com"),
        notion_email=EmailStr("notion@mail.com"),
        slack_email=EmailStr("slack@email.com"),
    )
    with pytest.raises(UserNotFoundException):
        user_service.update_invitaion_emails(user, request)


def test_partial_update_invitation_emails(
    created_user: User, user_service: UserService
):
    data = {
        "github_email": "github@email.com",
        "notion_email": "notion@email.com",
        "slack_email": "slack@email.com",
    }
    data = cast(dict[str, EmailStr], data)
    request = UserUpdateInvitationEmailsRequest(**data)
    user_service.update_invitaion_emails(created_user, request)

    # skip github_email update
    new_data = {
        "github_email": "new-github@email.com",
        "notion_email": None,
        "slack_email": None,
    }
    new_data = cast(dict[str, EmailStr], new_data)
    new_request = UserUpdateInvitationEmailsRequest(**new_data)
    user = user_service.update_invitaion_emails(created_user, new_request)
    assert (
        user.github_email == new_data["github_email"]
    ), "github_email should be updated"
    assert (
        user.notion_email == data["notion_email"]
    ), "notion_email should not be updated"
    assert user.slack_email == data["slack_email"], "slack_email should not be updated"
