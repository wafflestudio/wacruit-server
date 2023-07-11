from fastapi import HTTPException
import pytest

from wacruit.src.apps.user.schemas import UserCreateUpdateRequest
from wacruit.src.apps.user.services import UserService


def test_create_user(user_service: UserService):
    request = UserCreateUpdateRequest(
        sso_id="test",
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email="test@test.com",
    )
    response = user_service.create_user(request)
    assert response.id is not None


def test_create_user_duplicate_sso_id(user_service: UserService):
    request = UserCreateUpdateRequest(
        sso_id="test",
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email="test2@test.com",
    )
    user_service.create_user(request)
    with pytest.raises(HTTPException) as excinfo:
        new_request = request.copy()
        user_service.create_user(new_request)
        assert excinfo.value.status_code == 409


def test_create_user_duplicate_email(user_service: UserService):
    request = UserCreateUpdateRequest(
        sso_id="test2",
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email="test@test.com",
    )
    user_service.create_user(request)
    with pytest.raises(HTTPException) as excinfo:
        new_request = request.copy()
        user_service.create_user(new_request)
        assert excinfo.value.status_code == 409


def test_list_user_detail(user_service: UserService):
    request = UserCreateUpdateRequest(
        sso_id="test",
        first_name="test",
        last_name="test",
        phone_number="010-0000-0000",
        email="test@test.com",
    )
    response = user_service.create_user(request)
    assert response.id is not None

    users = user_service.list_users()
    assert len(users) == 1
    assert users[0].id == response.id
    assert users[0].sso_id == request.sso_id
