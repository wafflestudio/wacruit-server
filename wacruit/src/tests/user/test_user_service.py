from pydantic import EmailStr
import pytest

from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.exceptions import UserNotFoundException
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.schemas import UserCreateUpdateRequest
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.services import UserService


def test_create_user(user_service: UserService):
    request = UserCreateUpdateRequest(
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email=EmailStr("test@test.com"),
    )
    response = user_service.create_user("sso_id", request)
    assert response.id is not None


def test_create_user_duplicate_sso_id(user_service: UserService):
    sso_id = "test"
    request = UserCreateUpdateRequest(
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
    request = UserCreateUpdateRequest(
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email=EmailStr("test@test.com"),
    )
    user_service.create_user(sso_id, request)
    with pytest.raises(UserAlreadyExistsException):
        new_request = request.copy()
        user_service.create_user(sso_id, new_request)


def test_list_user_detail(user_service: UserService):
    sso_id = "test"
    request = UserCreateUpdateRequest(
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
