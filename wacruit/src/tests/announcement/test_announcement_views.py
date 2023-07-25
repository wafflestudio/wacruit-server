from fastapi.testclient import TestClient

from wacruit.src.apps.user.models import User


def test_cant_create_announcement_if_not_admin(user: User, test_client: TestClient):
    assert user.sso_id is not None
    assert user.is_admin is False
    response = test_client.post(
        "/api/v1/announcements/",
        json={
            "title": "title",
            "content": "content",
        },
        headers={"waffle-user-id": user.sso_id},
    )
    assert response.status_code == 403


def test_can_create_announcement_if_admin(admin_user: User, test_client: TestClient):
    assert admin_user.sso_id is not None
    assert admin_user.is_admin is True
    response = test_client.post(
        "/api/v1/announcements/",
        json={
            "title": "title",
            "content": "content",
        },
        headers={"waffle-user-id": admin_user.sso_id},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "title"
    assert response.json()["content"] == "content"
